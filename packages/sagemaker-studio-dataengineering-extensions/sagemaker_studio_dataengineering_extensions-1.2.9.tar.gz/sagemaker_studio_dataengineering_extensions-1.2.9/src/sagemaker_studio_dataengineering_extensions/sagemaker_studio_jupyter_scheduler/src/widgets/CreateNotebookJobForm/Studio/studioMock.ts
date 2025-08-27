import { KernelSpecResponse } from './studioModel';

export const StudioImagesMapResponseMock: KernelSpecResponse = {
  "default": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/2",
  "kernelspecs": {
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Data Science)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/1",
            "display_name": "Python 3 (arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/1)"
          },
          "instance_type": "ml.t3.medium"
        },
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/2": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/2",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Data Science)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/2",
            "display_name": "Python 3 (arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/2)"
          },
          "instance_type": "ml.t3.medium"
        },
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/python-3.6": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/python-3.6",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Base Python)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/python-3.6",
            "display_name": "Base Python",
            "description": "Official Python3.6 image from DockerHub https://hub.docker.com/_/python",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-38": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-38",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Base Python 2.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-38",
            "display_name": "Base Python 2.0",
            "description": "Official Python3.8 image from DockerHub https://hub.docker.com/_/python",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-310-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-310-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Base Python 3.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-base-python-310-v1",
            "display_name": "Base Python 3.0",
            "description": "Official Python 3.10 image from DockerHub https://hub.docker.com/_/python",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-data-science-38": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-data-science-38",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Data Science 2.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-data-science-38",
            "display_name": "Data Science 2.0",
            "description": "Official Python3.8 image from DockerHub https://hub.docker.com/_/python",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-data-science-310-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-data-science-310-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Data Science 3.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-data-science-310-v1",
            "display_name": "Data Science 3.0",
            "description": "Official Python 3.10 image from DockerHub https://hub.docker.com/_/python",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:081189585635:image/sagemaker-geospatial-v1-0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:081189585635:image/sagemaker-geospatial-v1-0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (Geospatial 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:081189585635:image/sagemaker-geospatial-v1-0",
            "display_name": "Geospatial 1.0",
            "description": "Python image for processing and visualizing geospatial data https://docs.aws.amazon.com/sagemaker/latest/dg/geospatial-notebook-sdk.html",
            "gpu_optimized": false,
            "is_template": true,
            "supported_instance_types": [
              "ml.geospatial.interactive"
            ]
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.6-cpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.6-cpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (MXNet 1.6 Python 3.6 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.6-cpu-py36",
            "display_name": "MXNet 1.6 Python 3.6 (optimized for CPU)",
            "description": "AWS Deep Learning Container for MXNet 1.6 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.6-gpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.6-gpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (MXNet 1.6 Python 3.6 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.6-gpu-py36",
            "display_name": "MXNet 1.6 Python 3.6 (optimized for GPU)",
            "description": "AWS Deep Learning Container for MXNet 1.6 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.8-cpu-py37-ubuntu16.04-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.8-cpu-py37-ubuntu16.04-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (MXNet 1.8 Python 3.7 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.8-cpu-py37-ubuntu16.04-v1",
            "display_name": "MXNet 1.8 Python 3.7 (optimized for CPU)",
            "description": "AWS Deep Learning Container for MXNet 1.8 Python 3.7 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.8-gpu-py37-cu110-ubuntu16.04-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.8-gpu-py37-cu110-ubuntu16.04-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (MXNet 1.8 Python 3.7 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.8-gpu-py37-cu110-ubuntu16.04-v1",
            "display_name": "MXNet 1.8 Python 3.7 (optimized for GPU)",
            "description": "AWS Deep Learning Container for MXNet 1.8 Python 3.7 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.9-cpu-py38-ubuntu20.04-sagemaker-v1.0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.9-cpu-py38-ubuntu20.04-sagemaker-v1.0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (MXNet 1.9 Python 3.8 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.9-cpu-py38-ubuntu20.04-sagemaker-v1.0",
            "display_name": "MXNet 1.9 Python 3.8 (optimized for CPU)",
            "description": "AWS Deep Learning Container for MXNet 1.9 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.9-gpu-py38-cu112-ubuntu20.04-sagemaker-v1.0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.9-gpu-py38-cu112-ubuntu20.04-sagemaker-v1.0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (MXNet 1.9 Python 3.8 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/mxnet-1.9-gpu-py38-cu112-ubuntu20.04-sagemaker-v1.0",
            "display_name": "MXNet 1.9 Python 3.8 (optimized for GPU)",
            "description": "AWS Deep Learning Container for MXNet 1.9 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.10-cpu-py38": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.10-cpu-py38",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.10 Python 3.8 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.10-cpu-py38",
            "display_name": "PyTorch 1.10 Python 3.8 (optimized for CPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.10 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.10-gpu-py38": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.10-gpu-py38",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.10 Python 3.8 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.10-gpu-py38",
            "display_name": "PyTorch 1.10 Python 3.8 (optimized for GPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.10 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.12-cpu-py38": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.12-cpu-py38",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.12 Python 3.8 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.12-cpu-py38",
            "display_name": "PyTorch 1.12 Python 3.8 (optimized for CPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.12 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.12-gpu-py38": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.12-gpu-py38",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.12 Python 3.8 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.12-gpu-py38",
            "display_name": "PyTorch 1.12 Python 3.8 (optimized for GPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.12 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.13-cpu-py39": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.13-cpu-py39",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.13 Python 3.9 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.13-cpu-py39",
            "display_name": "PyTorch 1.13 Python 3.9 (optimized for CPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.13 Python 3.9 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.13-gpu-py39": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.13-gpu-py39",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.13 Python 3.9 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.13-gpu-py39",
            "display_name": "PyTorch 1.13 Python 3.9 (optimized for GPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.13 Python 3.9 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.4-cpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.4-cpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.4 Python 3.6 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.4-cpu-py36",
            "display_name": "PyTorch 1.4 Python 3.6 (optimized for CPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.4 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.4-gpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.4-gpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.4 Python 3.6 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.4-gpu-py36",
            "display_name": "PyTorch 1.4 Python 3.6 (optimized for GPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.4 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.6-cpu-py36-ubuntu16.04-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.6-cpu-py36-ubuntu16.04-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.6 Python 3.6 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.6-cpu-py36-ubuntu16.04-v1",
            "display_name": "PyTorch 1.6 Python 3.6 (optimized for CPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.6 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.6-gpu-py36-cu110-ubuntu18.04-v3": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.6-gpu-py36-cu110-ubuntu18.04-v3",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.6 Python 3.6 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.6-gpu-py36-cu110-ubuntu18.04-v3",
            "display_name": "PyTorch 1.6 Python 3.6 (optimized for GPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.6 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/1.8.1-cpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/1.8.1-cpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.8 Python 3.6 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/1.8.1-cpu-py36",
            "display_name": "PyTorch 1.8 Python 3.6 (optimized for CPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.8 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.8-gpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.8-gpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (PyTorch 1.8 Python 3.6 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/pytorch-1.8-gpu-py36",
            "display_name": "PyTorch 1.8 Python 3.6 (optimized for GPU)",
            "description": "AWS Deep Learning Container for PyTorch 1.8 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-data-science-1.0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-data-science-1.0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (SageMaker JumpStart Data Science 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-data-science-1.0",
            "display_name": "SageMaker JumpStart Data Science 1.0",
            "description": "Only for use with Data Science based SageMaker JumpStart Solutions",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-mxnet-1.0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-mxnet-1.0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (SageMaker JumpStart MXNet 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-mxnet-1.0",
            "display_name": "SageMaker JumpStart MXNet 1.0",
            "description": "Only for use with MXNet based SageMaker JumpStart Solutions",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-pytorch-1.0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-pytorch-1.0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (SageMaker JumpStart PyTorch 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-pytorch-1.0",
            "display_name": "SageMaker JumpStart PyTorch 1.0",
            "description": "Only for use with PyTorch based SageMaker JumpStart Solutions",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-tensorflow-1.0": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-tensorflow-1.0",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (SageMaker JumpStart TensorFlow 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:787968894560:image/sagemaker-jumpstart-tensorflow-1.0",
            "display_name": "SageMaker JumpStart TensorFlow 1.0",
            "description": "Only for use with TensorFlow based SageMaker JumpStart Solutions",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_sparkmagic-sparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1": {
      "name": "conda-env-sm_sparkmagic-sparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "SparkMagic Spark (SparkAnalytics 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
            "display_name": "SparkAnalytics 1.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_sparkmagic-pysparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1": {
      "name": "conda-env-sm_sparkmagic-pysparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "SparkMagic PySpark (SparkAnalytics 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
            "display_name": "SparkAnalytics 1.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_glue_is-glue_spark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1": {
      "name": "conda-env-sm_glue_is-glue_spark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Glue Spark (SparkAnalytics 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
            "display_name": "SparkAnalytics 1.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_glue_is-glue_pyspark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1": {
      "name": "conda-env-sm_glue_is-glue_pyspark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Glue Python [PySpark and Ray] (SparkAnalytics 1.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-v1",
            "display_name": "SparkAnalytics 1.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_sparkmagic-sparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1": {
      "name": "conda-env-sm_sparkmagic-sparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "SparkMagic Spark (SparkAnalytics 2.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
            "display_name": "SparkAnalytics 2.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_sparkmagic-pysparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1": {
      "name": "conda-env-sm_sparkmagic-pysparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "SparkMagic PySpark (SparkAnalytics 2.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
            "display_name": "SparkAnalytics 2.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_glue_is-glue_spark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1": {
      "name": "conda-env-sm_glue_is-glue_spark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Glue Spark (SparkAnalytics 2.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
            "display_name": "SparkAnalytics 2.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "conda-env-sm_glue_is-glue_pyspark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1": {
      "name": "conda-env-sm_glue_is-glue_pyspark__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Glue PySpark (SparkAnalytics 2.0)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkanalytics-310-v1",
            "display_name": "SparkAnalytics 2.0",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "pysparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkmagic": {
      "name": "pysparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkmagic",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "PySpark (SparkMagic)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkmagic",
            "display_name": "SparkMagic",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "sparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkmagic": {
      "name": "sparkkernel__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkmagic",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Spark (SparkMagic)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/sagemaker-sparkmagic",
            "display_name": "SparkMagic",
            "description": "Anaconda Individual Edition with PySpark and Spark kernels. More details: https://github.com/jupyter-incubator/sparkmagic",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 1.15 Python 3.6 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py36",
            "display_name": "TensorFlow 1.15 Python 3.6 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 1.15 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-gpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-gpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 1.15 Python 3.6 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-gpu-py36",
            "display_name": "TensorFlow 1.15 Python 3.6 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 1.15 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py37-ubuntu18.04-v7": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py37-ubuntu18.04-v7",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 1.15 Python 3.7 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py37-ubuntu18.04-v7",
            "display_name": "TensorFlow 1.15 Python 3.7 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 1.15 Python 3.7 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-gpu-py37-cu110-ubuntu18.04-v8": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-gpu-py37-cu110-ubuntu18.04-v8",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 1.15 Python 3.7 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-gpu-py37-cu110-ubuntu18.04-v8",
            "display_name": "TensorFlow 1.15 Python 3.7 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 1.15 Python 3.7 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-cpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-cpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.1 Python 3.6 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-cpu-py36",
            "display_name": "TensorFlow 2.1 Python 3.6 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.1 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-gpu-py36": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-gpu-py36",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.1 Python 3.6 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-gpu-py36",
            "display_name": "TensorFlow 2.1 Python 3.6 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.1 Python 3.6 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.10-cpu-py39-ubuntu20.04-sagemaker-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.10-cpu-py39-ubuntu20.04-sagemaker-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.10.0 Python 3.9 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.10-cpu-py39-ubuntu20.04-sagemaker-v1",
            "display_name": "TensorFlow 2.10 Python 3.9 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.10 Python 3.9 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.10-gpu-py39-cu112-ubuntu20.04-sagemaker-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.10-gpu-py39-cu112-ubuntu20.04-sagemaker-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.10.0 Python 3.9 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.10-gpu-py39-cu112-ubuntu20.04-sagemaker-v1",
            "display_name": "TensorFlow 2.10 Python 3.9 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.10 Python 3.9 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.11.0-cpu-py39-ubuntu20.04-sagemaker-v1.1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.11.0-cpu-py39-ubuntu20.04-sagemaker-v1.1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.11.0 Python 3.9 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.11.0-cpu-py39-ubuntu20.04-sagemaker-v1.1",
            "display_name": "TensorFlow 2.11 Python 3.9 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.11 Python 3.9 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.11.0-gpu-py39-cu112-ubuntu20.04-sagemaker-v1.1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.11.0-gpu-py39-cu112-ubuntu20.04-sagemaker-v1.1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.11.0 Python 3.9 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.11.0-gpu-py39-cu112-ubuntu20.04-sagemaker-v1.1",
            "display_name": "TensorFlow 2.11 Python 3.9 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.11 Python 3.9 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-cpu-py37-ubuntu18.04-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-cpu-py37-ubuntu18.04-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.3 Python 3.7 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-cpu-py37-ubuntu18.04-v1",
            "display_name": "TensorFlow 2.3 Python 3.7 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.3 Python 3.7 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-gpu-py37-cu110-ubuntu18.04-v3": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-gpu-py37-cu110-ubuntu18.04-v3",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.3 Python 3.7 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-gpu-py37-cu110-ubuntu18.04-v3",
            "display_name": "TensorFlow 2.3 Python 3.7 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.3 Python 3.7 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.6-cpu-py38-ubuntu20.04-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.6-cpu-py38-ubuntu20.04-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.6 Python 3.8 CPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.6-cpu-py38-ubuntu20.04-v1",
            "display_name": "TensorFlow 2.6 Python 3.8 (optimized for CPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.6 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": false,
            "is_template": true
          },
          "instance_type": "ml.t3.medium"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    },
    "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1": {
      "name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1",
      "spec": {
        "argv": [
          "python3",
          "-m",
          "IPython.kernel",
          "-f",
          "{connection_file}"
        ],
        "display_name": "Python 3 (TensorFlow 2.6 Python 3.8 GPU Optimized)",
        "language": "python",
        "metadata": {
          "sme_metadata": {
            "environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1",
            "display_name": "TensorFlow 2.6 Python 3.8 (optimized for GPU)",
            "description": "AWS Deep Learning Container for TensorFlow 2.6 Python 3.8 https://docs.aws.amazon.com/dlami/latest/devguide/deep-learning-containers-images.html",
            "gpu_optimized": true,
            "is_template": true
          },
          "instance_type": "ml.g4dn.xlarge"
        }
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png",
        "logo-32x32": "/kernelspecs/python3/logo-32x32.png"
      }
    }
  }
};
