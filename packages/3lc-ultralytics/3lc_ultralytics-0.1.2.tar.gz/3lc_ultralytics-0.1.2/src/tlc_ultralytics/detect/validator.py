from __future__ import annotations

import weakref

import tlc
import torch
from ultralytics.models.yolo.detect import DetectionValidator
from ultralytics.utils import metrics, ops

from tlc_ultralytics.constants import (
    DETECTION_LABEL_COLUMN_NAME,
    IMAGE_COLUMN_NAME,
)
from tlc_ultralytics.detect.loss import v8UnreducedDetectionLoss
from tlc_ultralytics.detect.utils import (
    build_tlc_yolo_dataset,
    construct_bbox_struct,
    tlc_check_det_dataset,
    yolo_loss_schemas,
    yolo_predicted_bounding_box_schema,
)
from tlc_ultralytics.engine.validator import TLCValidatorMixin


class TLCDetectionValidator(TLCValidatorMixin, DetectionValidator):
    _default_image_column_name = IMAGE_COLUMN_NAME
    _default_label_column_name = DETECTION_LABEL_COLUMN_NAME

    def check_dataset(self, *args, **kwargs):
        return tlc_check_det_dataset(*args, **kwargs)

    def build_dataset(self, table, mode="val", batch=None):
        return build_tlc_yolo_dataset(
            self.args,
            table,
            batch,
            self.data,
            mode=mode,
            stride=self.stride,
            exclude_zero=self._settings.exclude_zero_weight_collection,
            class_map=self.data["3lc_class_to_range"],
            split=self.args.split,
            image_column_name=self._image_column_name,
            label_column_name=self._label_column_name,
        )

    def postprocess(self, preds):
        self._curr_raw_preds = preds if self._settings.collect_loss else None
        return super().postprocess(preds)

    def _get_metrics_schemas(self):
        loss_schemas = yolo_loss_schemas(training=self._training) if self._settings.collect_loss else {}

        return {
            tlc.PREDICTED_BOUNDING_BOXES: yolo_predicted_bounding_box_schema(self.data["names_3lc"]),
            **loss_schemas,
        }

    def _compute_3lc_metrics(self, preds, batch):
        losses = self.loss_fn(self._curr_raw_preds, batch) if self._settings.collect_loss else {}

        processed_predictions = self._process_detection_predictions(preds, batch)
        return {
            tlc.PREDICTED_BOUNDING_BOXES: processed_predictions,
            **{k: tensor.mean(dim=1).cpu().numpy() for k, tensor in losses.items()},
        }

    def _process_detection_predictions(self, preds, batch):
        predicted_boxes = []
        for i, predictions in enumerate(preds):
            ori_shape = batch["ori_shape"][i]
            resized_shape = batch["resized_shape"][i]
            ratio_pad = batch["ratio_pad"][i]
            height, width = ori_shape

            # Handle case with no predictions
            if len(predictions) == 0:
                predicted_boxes.append(
                    construct_bbox_struct(
                        [],
                        image_width=width,
                        image_height=height,
                    )
                )
                continue

            predictions = predictions.clone()
            predictions = predictions[
                predictions[:, 4] > self._settings.conf_thres
            ]  # filter out low confidence predictions
            # sort by confidence and remove excess boxes
            predictions = predictions[predictions[:, 4].argsort(descending=True)[: self._settings.max_det]]

            pred_box = predictions[:, :4].clone()
            pred_scaled = ops.scale_boxes(resized_shape, pred_box, ori_shape, ratio_pad)

            # Compute IoUs
            pbatch = self._prepare_batch(i, batch)
            if pbatch["bbox"].shape[0]:
                ious = metrics.box_iou(pbatch["bbox"], pred_scaled)  # IoU evaluated in xyxy format
                box_ious = ious.max(dim=0)[0].cpu().tolist()
            else:
                box_ious = [0.0] * pred_scaled.shape[0]  # No predictions

            pred_xywh = ops.xyxy2xywhn(pred_scaled, w=width, h=height)

            conf = predictions[:, 4].cpu().tolist()
            pred_cls = predictions[:, 5].cpu().tolist()

            annotations = []
            for pi in range(len(predictions)):
                annotations.append(
                    {
                        "score": conf[pi],
                        "category_id": self.data["range_to_3lc_class"][int(pred_cls[pi])],
                        "bbox": pred_xywh[pi, :].cpu().tolist(),
                        "iou": box_ious[pi],
                    }
                )

            assert len(annotations) <= self._settings.max_det, "Should have at most MAX_DET predictions per image."

            predicted_boxes.append(
                construct_bbox_struct(
                    annotations,
                    image_width=width,
                    image_height=height,
                )
            )

        return predicted_boxes

    def _prepare_loss_fn(self, model):
        self.loss_fn = v8UnreducedDetectionLoss(
            model.model if hasattr(model.model, "model") else model,
            training=self._training,
        )

    def _add_embeddings_hook(self, model) -> int:
        if hasattr(model.model, "model"):
            model = model.model

        # Find index of the SPPF layer
        sppf_index = next((i for i, m in enumerate(model.model) if "SPPF" in m.type), -1)

        if sppf_index == -1:
            raise ValueError(
                "Image level embeddings can only be collected for detection models with a SPPF layer, "
                "but this model does not have one."
            )

        weak_self = weakref.ref(self)  # Avoid circular reference (self <-> hook_fn)

        def hook_fn(_module, _input, output):
            # Store embeddings
            self_ref = weak_self()
            flattened_output = torch.nn.functional.adaptive_avg_pool2d(output, (1, 1)).squeeze(-1).squeeze(-1)
            embeddings = flattened_output.detach().cpu().numpy()
            self_ref.embeddings = embeddings

        # Add forward hook to collect embeddings
        for i, module in enumerate(model.model):
            if i == sppf_index:
                self._hook_handles.append(module.register_forward_hook(hook_fn))

        activation_size = model.model[sppf_index]._modules["cv2"]._modules["conv"].out_channels
        return activation_size

    def _infer_batch_size(self, preds, batch) -> int:
        return len(batch["im_file"])
