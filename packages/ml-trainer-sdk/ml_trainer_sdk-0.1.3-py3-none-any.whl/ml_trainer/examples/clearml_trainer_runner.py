import torch
import ast
from clearml import Task, OutputModel
from ml_trainer.auto_trainer import AutoTrainer


def run_clearml_training(project_name: str, task_name: str, config: dict):
    # Initialize ClearML task
    task = Task.init(project_name=project_name, task_name=task_name, task_type=Task.TaskTypes.training)

    # Log original config to ClearML
    task.connect(config)

    # Train
    trainer = AutoTrainer(config=config)
    trainer.run()

    # Save and upload model
    model_path = "model.pt"
    torch.save(trainer.trainer.model.state_dict(), model_path)

    output_model = OutputModel(task=task, framework="pytorch")
    output_model.update_weights(weights_filename=model_path)

    task.close()
    print(f"[✅] Task '{task_name}' completed and model uploaded.")
