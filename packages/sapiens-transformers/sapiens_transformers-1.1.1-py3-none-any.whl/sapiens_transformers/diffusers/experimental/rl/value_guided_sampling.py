'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from ...utils.dummy_pt_objects import DDPMScheduler
from ...models.unets.unet_1d import UNet1DModel
from ...utils.torch_utils import randn_tensor
from ...pipelines import DiffusionPipeline
import numpy as np
import torch
import tqdm
class ValueGuidedRLPipeline(DiffusionPipeline):
    def __init__(self, value_function: UNet1DModel, unet: UNet1DModel, scheduler: DDPMScheduler, env):
        super().__init__()
        self.register_modules(value_function=value_function, unet=unet, scheduler=scheduler, env=env)
        self.data = env.get_dataset()
        self.means = {}
        for key in self.data.keys():
            try: self.means[key] = self.data[key].mean()
            except: pass
        self.stds = {}
        for key in self.data.keys():
            try: self.stds[key] = self.data[key].std()
            except: pass
        self.state_dim = env.observation_space.shape[0]
        self.action_dim = env.action_space.shape[0]
    def normalize(self, x_in, key): return (x_in - self.means[key]) / self.stds[key]
    def de_normalize(self, x_in, key): return x_in * self.stds[key] + self.means[key]
    def to_torch(self, x_in):
        if isinstance(x_in, dict): return {k: self.to_torch(v) for k, v in x_in.items()}
        elif torch.is_tensor(x_in): return x_in.to(self.unet.device)
        return torch.tensor(x_in, device=self.unet.device)
    def reset_x0(self, x_in, cond, act_dim):
        for key, val in cond.items(): x_in[:, key, act_dim:] = val.clone()
        return x_in
    def run_diffusion(self, x, conditions, n_guide_steps, scale):
        batch_size = x.shape[0]
        y = None
        for i in tqdm.tqdm(self.scheduler.timesteps):
            timesteps = torch.full((batch_size,), i, device=self.unet.device, dtype=torch.long)
            for _ in range(n_guide_steps):
                with torch.enable_grad():
                    x.requires_grad_()
                    y = self.value_function(x.permute(0, 2, 1), timesteps).sample
                    grad = torch.autograd.grad([y.sum()], [x])[0]
                    posterior_variance = self.scheduler._get_variance(i)
                    model_std = torch.exp(0.5 * posterior_variance)
                    grad = model_std * grad
                grad[timesteps < 2] = 0
                x = x.detach()
                x = x + scale * grad
                x = self.reset_x0(x, conditions, self.action_dim)
            prev_x = self.unet(x.permute(0, 2, 1), timesteps).sample.permute(0, 2, 1)
            x = self.scheduler.step(prev_x, i, x)['prev_sample']
            x = self.reset_x0(x, conditions, self.action_dim)
            x = self.to_torch(x)
        return (x, y)
    def __call__(self, obs, batch_size=64, planning_horizon=32, n_guide_steps=2, scale=0.1):
        obs = self.normalize(obs, 'observations')
        obs = obs[None].repeat(batch_size, axis=0)
        conditions = {0: self.to_torch(obs)}
        shape = (batch_size, planning_horizon, self.state_dim + self.action_dim)
        x1 = randn_tensor(shape, device=self.unet.device)
        x = self.reset_x0(x1, conditions, self.action_dim)
        x = self.to_torch(x)
        x, y = self.run_diffusion(x, conditions, n_guide_steps, scale)
        sorted_idx = y.argsort(0, descending=True).squeeze()
        sorted_values = x[sorted_idx]
        actions = sorted_values[:, :, :self.action_dim]
        actions = actions.detach().cpu().numpy()
        denorm_actions = self.de_normalize(actions, key='actions')
        if y is not None: selected_index = 0
        else: selected_index = np.random.randint(0, batch_size)
        denorm_actions = denorm_actions[selected_index, 0]
        return denorm_actions
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
