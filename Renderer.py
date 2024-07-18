import numpy as np
import torch


class Renderer:
    def __init__(self, resolution: int, steps_per_frame: int = 10, threshold: float = 1.e-3) -> None:
        self.threshold: float = threshold
        self.resolution: int = resolution
        self.steps_per_frame: int = steps_per_frame
        self.display: torch.tensor = torch.linspace(-1, 1, steps=resolution)
        self.display = torch.cartesian_prod(self.display, self.display, torch.tensor([2], dtype=torch.float32))
        self.display = self.display.cuda()
        self.ray_dirs = torch.nn.functional.normalize(self.display)

    def sdf(self, rays: torch.tensor, objects: list[torch.tensor]) -> torch.tensor:
        min_sdf = objects[0].sdf(rays)
        for obj in objects[1:]:
            min_sdf = torch.minimum(min_sdf, obj.sdf(rays))
        return min_sdf.unsqueeze(1)

    def get_frame(self, objects: list[torch.tensor]) -> np.ndarray:
        rays = self.display.clone()
        for i in range(10):
            rays += self.ray_dirs * self.sdf(rays, objects)
        return self.sdf(rays, objects).detach().cpu().apply_(lambda x: 1 if x < self.threshold else 0).numpy()
