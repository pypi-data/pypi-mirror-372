# !/usr/bin/env python
# -*-coding:utf-8 -*-
# import sys
# sys.path.append("/data3/leizhiming/arcternweb_sdk")

import unittest
import json
from pathlib import Path
from arcternweb.client import Client


BASE_URL = "http://192.168.99.63:30026"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJYLXVpZCI6MTQ3LCJleHAiOjIzODYzMDgxOTgsImlhdCI6MTc1NTU4ODE5OH0.ZRnHmTmbwvxdrvhX4qZfPqSCafvNf3I-JduQ7EEBHnI"


class TestArcternweb(unittest.TestCase):
    def test_classifier(self):
        client = Client(base_url=BASE_URL, token=TOKEN)
        infer_task_id = 13002  # 12811 #5186
        try:
            infer_task_info = client.infer_task_server.get(infer_task_id)
            print(infer_task_info)
        except Exception as e:
            print(f"infer_task_server error: {e}")
            return

        if infer_task_info:
            try:
                model_group_info = client.model_group_server.get(infer_task_info.model_group_id)
                print(model_group_info)
            except Exception as e:
                print(f"model_group_server error: {e}")

            bin_name = Path(infer_task_info.result_path).stem
            print("bin_name: ", bin_name)

            ok = client.utils.download_file(infer_task_info.result_path, "data/result.json")
            if ok:
                print("download file " + infer_task_info.result_path + " success")
            else:
                print("download file " + infer_task_info.result_path + " failed")

        predicts = client.classifier_utils.parse_infers_from_result_file("data/result.json")
        if not predicts:
            print("parse_infers_from_result_file failed")
        else:
            print("predicts: ", predicts)

        label = [{"color": ["red", "green", "blue"]}, {"shape": ["rectangle", "triangle", "circle"]}]
        # label = [{"Smoke": ["no", "yes"]}]
        # label = json.loads(infer_task_info.label)
        print(label)
        gt = client.classifier_utils.parse_labels_from_result_file("data/result.json", label)
        if not gt:
            print("parse_labels_from_result_file failed")
        else:
            print("gt: ", gt)

        if predicts and gt:
            from sklearn.metrics import classification_report

            supercats = []
            cats = []
            for group in label:
                for supercat, names in group.items():
                    supercats.append(supercat)
                    cats.append(names)
            print("supercats: ", supercats)
            print("cats: ", cats)
            reports = {}
            reports["report"] = []
            reports["info"] = {}
            for idx, supercat in enumerate(supercats):
                print("gt len: ", len(gt[idx]))
                print("predicts len: ", len(predicts[idx]))
                print("cats lens: ", len(cats[idx]))
                idx_labels = list(range(len(cats[idx])))
                print(idx_labels)
                report = classification_report(
                    gt[idx], predicts[idx], digits=4, target_names=cats[idx], output_dict=True, labels=idx_labels
                )
                reports["report"].append({supercats[idx]: report})
                reports["info"]["model_group_id"] = model_group_info.m_model_group_id
                reports["info"]["model_name"] = bin_name
                reports["info"]["dataset_id"] = infer_task_info.dataset_id
                reports["info"]["dataset_name"] = infer_task_info.dataset_name

            print(reports)
            Path("data/metrics.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")

        ok = client.classifier_utils.to_COCO("data/result.json", label, "data/coco_gt.json", "data/coco_dt.json")
        if ok:
            print("arcternweb to coco dataset success")
        else:
            print("arcternweb to coco dataset failed")

        # images = client.utils.parse_images_from_result_file("data/result.json")
        # if not images:
        #     print("parse_images_from_result_file failed")
        # else:
        #     print("images: ", images)

    # def test_detector(self):
    #     from pycocotools.coco import COCO
    #     from pycocotools.cocoeval import COCOeval

    #     ann_file = "data/coco_gt.json"
    #     res_file = "data/coco_dt.json"
    #     coco_gt = COCO(ann_file)
    #     coco_dt = coco_gt.loadRes(res_file)

    #     coco_eval = COCOeval(coco_gt, coco_dt, iouType="bbox")

    #     coco_eval.params.imgIds = coco_gt.getImgIds()

    #     coco_eval.evaluate()
    #     coco_eval.accumulate()
    #     coco_eval.summarize()


if __name__ == "__main__":
    unittest.main()
