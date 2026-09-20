import tempfile
import os
import cv2
import torch
import numpy as np
import gradio as gr
from anomalib.models import Padim
from anomalib.engine import Engine
from anomalib.data import PredictDataset
from torch.utils.data import DataLoader
from pathlib import Path
from huggingface_hub import hf_hub_download

CKPT_PATH = hf_hub_download(
    repo_id="KietDo/padim-mvtec-leather",
    filename="model.ckpt"
)

model = Padim.load_from_checkpoint(CKPT_PATH, weights_only=False)
engine = Engine(
    callbacks=[],
    logger=False,
)

def predict(image):
    if not image:
        return
    
    temp_image_path = ""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_image_path = os.path.join(temp_dir, "temp_img.png")

        image.save(temp_image_path)

        dataset = PredictDataset(
            path = temp_image_path,
            image_size = (256,256)
        )

        data_loader = DataLoader(
            dataset=dataset,
            batch_size=1,
            num_workers = 0
        )

        predictions = engine.predict(model=model, dataloaders=data_loader)

        prediction = predictions[0]

        pred_score = prediction['pred_scores']
        anomaly_map = prediction['anomaly_maps']
        pred_label = prediction['pred_labels']

        anomaly_map = anomaly_map.cpu().numpy()

        map = anomaly_map.squeeze()
        map_normalized = (map - map.min()) / (map.max() - map.min())
        map_scaled = (map_normalized * 255).astype(np.uint8)

        np_rgb = np.array(image)
        img_bgr = cv2.cvtColor(np_rgb, cv2.COLOR_RGB2BGR)

        h, w = img_bgr.shape[:2]
        heatmap_bgr = cv2.applyColorMap(map_scaled, cv2.COLORMAP_JET)
        heatmap_bgr = cv2.resize(heatmap_bgr, (w, h))

        output_img = cv2.addWeighted(img_bgr, 0.6, heatmap_bgr, 0.4, 0)

        blend = cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB)

        status_string = "Anomalous" if pred_label.item() == 1 else "Normal"

        return (blend, status_string, float(pred_score))



with gr.Blocks(title="Leather Defect Detector") as demo:
    gr.Markdown("# Leather Anomaly Detector\nPaDiM model trained on MVTec leather. Image AUROC: 1.00 | Pixel AUROC: 0.99")
    
    with gr.Row():
        input_image = gr.Image(type="pil", label="Upload Leather Image")
        output_image = gr.Image(type="numpy", label="Anomaly Heatmap")
    
    with gr.Row():
        status = gr.Textbox(label="Status")
        score = gr.Number(label="Anomaly Score")
    
    btn = gr.Button("Detect", variant="primary")
    btn.click(fn=predict, inputs=input_image, outputs=[output_image, status, score])

demo.launch(server_name="0.0.0.0", server_port=7860)