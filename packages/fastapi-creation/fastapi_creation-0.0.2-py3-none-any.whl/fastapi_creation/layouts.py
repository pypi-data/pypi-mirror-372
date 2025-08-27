"""
This module defines the folder and file structure for different FastAPI project architectures.
Each architecture is stored as a nested dictionary where keys are folder or file names,
and values are either:
- another dictionary (for a folder),
- an empty string or content (for a file).
"""

LAYOUTS = {
    # 1. Simple / Flat Structure
    "simple": {
        "main.py": "",
        "requirements.txt": "",
        ".env": "",
        "README.md": "# Simple FastAPI Project"
    },

    # 2. Basic Modular Structure
    "modular": {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "models.py": "",
            "routes.py": "",
            "schemas.py": "",
            "database.py": "",
            "config.py": ""
        },
        "tests": {
            "test_main.py": "",
            "test_routes.py": ""
        },
        "requirements.txt": "",
        ".env": "",
        "README.md": "# Basic Modular FastAPI Project"
    },

    # 3. Domain-Driven Structure
    "ddd": {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "core": {
                "__init__.py": "",
                "config.py": "",
                "database.py": "",
                "security.py": "",
                "dependencies.py": ""
            },
            "users": {
                "__init__.py": "",
                "models.py": "",
                "routes.py": "",
                "schemas.py": "",
                "services.py": "",
                "dependencies.py": ""
            },
            "products": {
                "__init__.py": "",
                "models.py": "",
                "routes.py": "",
                "schemas.py": "",
                "services.py": ""
            },
            "shared": {
                "__init__.py": "",
                "utils.py": "",
                "exceptions.py": ""
            }
        },
        "tests": {
            "users": {},
            "products": {}
        },
        "requirements.txt": "",
        ".env": "",
        "README.md": "# Domain-Driven FastAPI Project"
    },

    # 4. Layered Architecture
    "layered": {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "api": {
                "__init__.py": "",
                "v1": {
                    "__init__.py": "",
                    "endpoints": {
                        "users.py": "",
                        "products.py": ""
                    },
                    "router.py": ""
                },
                "dependencies.py": ""
            },
            "core": {
                "__init__.py": "",
                "config.py": "",
                "database.py": "",
                "security.py": ""
            },
            "models": {
                "__init__.py": "",
                "user.py": "",
                "product.py": ""
            },
            "schemas": {
                "__init__.py": "",
                "user.py": "",
                "product.py": ""
            },
            "services": {
                "__init__.py": "",
                "user_service.py": "",
                "product_service.py": ""
            },
            "repositories": {
                "__init__.py": "",
                "user_repository.py": "",
                "product_repository.py": ""
            }
        },
        "tests": {},
        "requirements.txt": "",
        ".env": "",
        "README.md": "# Layered FastAPI Project"
    },

    # 5. Clean Architecture
    "clean": {
        "src": {
            "domain": {
                "__init__.py": "",
                "entities": {
                    "user.py": "",
                    "product.py": ""
                },
                "repositories": {
                    "user_repository.py": "",
                    "product_repository.py": ""
                },
                "services": {
                    "user_domain_service.py": "",
                    "product_domain_service.py": ""
                }
            },
            "application": {
                "__init__.py": "",
                "use_cases": {
                    "user": {
                        "create_user.py": "",
                        "get_user.py": ""
                    },
                    "product": {}
                },
                "services": {
                    "application_service.py": ""
                }
            },
            "infrastructure": {
                "__init__.py": "",
                "database": {
                    "models.py": "",
                    "connection.py": ""
                },
                "repositories": {
                    "sqlalchemy_user_repository.py": "",
                    "sqlalchemy_product_repository.py": ""
                },
                "external": {
                    "email_service.py": ""
                }
            },
            "presentation": {
                "__init__.py": "",
                "api": {
                    "v1": {
                        "users.py": "",
                        "products.py": ""
                    },
                    "dependencies.py": ""
                },
                "schemas": {
                    "user_schemas.py": "",
                    "product_schemas.py": ""
                }
            }
        },
        "tests": {},
        "main.py": "",
        "requirements.txt": "",
        "README.md": "# Clean Architecture FastAPI Project"
    },

    # 6. Microservices Structure
    "microservices": {
        "services": {
            "user_service": {
                "app": {
                    "main.py": "",
                    "models.py": "",
                    "routes.py": ""
                },
                "Dockerfile": "",
                "requirements.txt": "",
                ".env": ""
            },
            "product_service": {
                "app": {
                    "main.py": "",
                    "models.py": "",
                    "routes.py": ""
                },
                "Dockerfile": "",
                "requirements.txt": "",
                ".env": ""
            },
            "notification_service": {
                "app": {},
                "Dockerfile": "",
                "requirements.txt": ""
            }
        },
        "shared": {
            "models": {
                "common.py": ""
            },
            "utils": {
                "helpers.py": ""
            },
            "middleware": {}
        },
        "gateway": {
            "main.py": "",
            "routes.py": "",
            "middleware.py": ""
        },
        "docker-compose.yml": "",
        "kubernetes": {
            "deployment.yaml": "",
            "service.yaml": ""
        },
        "README.md": "# Microservices FastAPI Project"
    },

    # 7. Feature-Based Structure
    "feature": {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "core": {
                "config.py": "",
                "database.py": "",
                "security.py": ""
            },
            "features": {
                "__init__.py": "",
                "authentication": {
                    "__init__.py": "",
                    "routes.py": "",
                    "models.py": "",
                    "services.py": "",
                    "schemas.py": "",
                    "dependencies.py": ""
                },
                "user_management": {
                    "__init__.py": "",
                    "routes.py": "",
                    "models.py": "",
                    "services.py": "",
                    "schemas.py": ""
                },
                "payment": {
                    "__init__.py": "",
                    "routes.py": "",
                    "models.py": "",
                    "services.py": ""
                },
                "reporting": {
                    "__init__.py": "",
                    "routes.py": "",
                    "services.py": ""
                }
            },
            "shared": {
                "utils.py": "",
                "exceptions.py": "",
                "middleware.py": ""
            }
        },
        "tests": {
            "features": {
                "test_authentication.py": "",
                "test_user_management.py": "",
                "test_payment.py": ""
            }
        },
        "requirements.txt": "",
        ".env": "",
        "README.md": "# Feature-Based FastAPI Project"
    },

    # 8. Hexagonal Architecture
    "hexagonal": {
        "src": {
            "adapters": {
                "__init__.py": "",
                "inbound": {
                    "__init__.py": "",
                    "web": {
                        "fastapi_adapter.py": "",
                        "routes": {
                            "user_routes.py": "",
                            "product_routes.py": ""
                        },
                        "schemas": {}
                    }
                },
                "outbound": {
                    "__init__.py": "",
                    "database": {
                        "sqlalchemy_adapter.py": "",
                        "models.py": ""
                    },
                    "external": {
                        "email_adapter.py": "",
                        "payment_adapter.py": ""
                    },
                    "cache": {
                        "redis_adapter.py": ""
                    }
                }
            },
            "application": {
                "__init__.py": "",
                "ports": {
                    "__init__.py": "",
                    "inbound": {
                        "user_service_port.py": "",
                        "product_service_port.py": ""
                    },
                    "outbound": {
                        "user_repository_port.py": "",
                        "email_service_port.py": "",
                        "cache_port.py": ""
                    }
                },
                "services": {
                    "__init__.py": "",
                    "user_service.py": "",
                    "product_service.py": ""
                }
            },
            "domain": {
                "__init__.py": "",
                "entities": {
                    "user.py": "",
                    "product.py": ""
                },
                "value_objects": {
                    "email.py": "",
                    "money.py": ""
                },
                "exceptions": {
                    "domain_exceptions.py": "",
                    "validation_exceptions.py": ""
                }
            }
        },
        "tests": {
            "unit": {},
            "integration": {},
            "acceptance": {}
        },
        "main.py": "",
        "requirements.txt": "",
        "README.md": "# Hexagonal FastAPI Project"
    }
}
