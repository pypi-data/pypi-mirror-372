from ipykernel.kernelapp import IPKernelApp
from . import VMKernel

IPKernelApp.launch_instance(kernel_class=VMKernel)
