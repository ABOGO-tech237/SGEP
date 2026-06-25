from __future__ import annotations


def build_student_openapi_schema() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "SGEP Students API",
            "version": "1.0.0",
            "description": "Documentation Swagger du flux eleve, incluant le lien parent/eleve.",
        },
        "security": [{"bearerAuth": []}],
        "paths": {
            "/api/v1/students/": {
                "get": {
                    "summary": "Lister les eleves",
                    "tags": ["Students"],
                    "operationId": "listStudents",
                    "responses": {
                        "200": {
                            "description": "Liste paginee des eleves.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/StudentListResponse"}
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Creer un eleve et son compte parent",
                    "tags": ["Students"],
                    "operationId": "createStudent",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StudentCreate"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Eleve cree avec liaison parent.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Student"}
                                }
                            },
                        }
                    },
                },
            },
            "/api/v1/students/{student_id}/": {
                "get": {
                    "summary": "Lire un eleve",
                    "tags": ["Students"],
                    "operationId": "retrieveStudent",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Detail de l'eleve.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Student"}
                                }
                            },
                        }
                    },
                },
                "patch": {
                    "summary": "Mettre a jour un eleve",
                    "tags": ["Students"],
                    "operationId": "updateStudent",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StudentCreate"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Eleve mis a jour.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Student"}
                                }
                            },
                        }
                    },
                },
                "delete": {
                    "summary": "Supprimer un eleve",
                    "tags": ["Students"],
                    "operationId": "deleteStudent",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"204": {"description": "Eleve supprime."}},
                },
            },
            "/api/v1/students/{student_id}/history/": {
                "get": {
                    "summary": "Historique d'un eleve",
                    "tags": ["Students"],
                    "operationId": "listStudentHistory",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Historique de l'eleve.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/StudentHistoryList"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/students/{student_id}/enroll/": {
                "post": {
                    "summary": "Inscrire un eleve dans une classe",
                    "tags": ["Students"],
                    "operationId": "enrollStudent",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StudentEnroll"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Eleve inscrite.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Student"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/students/{student_id}/promote/": {
                "post": {
                    "summary": "Promouvoir un eleve",
                    "tags": ["Students"],
                    "operationId": "promoteStudent",
                    "parameters": [
                        {
                            "name": "student_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StudentPromote"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Eleve promu.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Student"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/students/export/pdf/": {
                "get": {
                    "summary": "Exporter les eleves en PDF",
                    "tags": ["Students"],
                    "operationId": "exportStudentsPdf",
                    "responses": {
                        "202": {
                            "description": "Job d'export lance.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ExportJobResponse"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/students/export/excel/": {
                "get": {
                    "summary": "Exporter les eleves en Excel",
                    "tags": ["Students"],
                    "operationId": "exportStudentsExcel",
                    "responses": {
                        "202": {
                            "description": "Job d'export lance.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ExportJobResponse"}
                                }
                            },
                        }
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {
                "Student": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "matricule": {"type": "string"},
                        "birth_date": {"type": "string", "format": "date-time"},
                        "birth_place": {"type": "string"},
                        "gender": {"type": "string"},
                        "id_number": {"type": "string", "nullable": True},
                        "medical": {"type": "object", "nullable": True},
                        "school_id": {"type": "string", "nullable": True},
                        "class_id": {"type": "string", "nullable": True},
                        "academic_year_id": {"type": "string", "nullable": True},
                        "current_level_id": {"type": "string", "nullable": True},
                        "parent_user_id": {"type": "string", "nullable": True},
                        "is_active": {"type": "boolean"},
                        "is_deleted": {"type": "boolean"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                    },
                },
                "StudentListResponse": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/StudentListItem"},
                        },
                    },
                },
                "StudentListItem": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "matricule": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "class_id": {"type": "string", "nullable": True},
                        "academic_year_id": {"type": "string", "nullable": True},
                        "current_level_id": {"type": "string", "nullable": True},
                        "is_active": {"type": "boolean"},
                    },
                },
                "StudentHistoryList": {
                    "type": "array",
                    "items": {"type": "object"},
                },
                "ExportJobResponse": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string"},
                    },
                },
                "StudentCreate": {
                    "type": "object",
                    "required": [
                        "first_name",
                        "last_name",
                        "matricule",
                        "birth_date",
                        "birth_place",
                        "gender",
                    ],
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "matricule": {"type": "string"},
                        "birth_date": {"type": "string", "format": "date-time"},
                        "birth_place": {"type": "string"},
                        "gender": {"type": "string"},
                        "medical": {"type": "object", "nullable": True},
                        "school_id": {"type": "string", "nullable": True},
                        "class_id": {"type": "string", "nullable": True},
                        "academic_year_id": {"type": "string", "nullable": True},
                        "current_level_id": {"type": "string", "nullable": True},
                        "parent": {"$ref": "#/components/schemas/ParentInput"},
                    },
                },
                "ParentInput": {
                    "type": "object",
                    "required": ["first_name", "last_name", "relationship", "phone", "email"],
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "relationship": {"type": "string"},
                        "phone": {"type": "string"},
                        "phone2": {"type": "string", "nullable": True},
                        "email": {"type": "string", "format": "email"},
                    },
                },
                "StudentEnroll": {
                    "type": "object",
                    "required": ["class_id", "academic_year_id"],
                    "properties": {
                        "class_id": {"type": "string"},
                        "academic_year_id": {"type": "string"},
                    },
                },
                "StudentPromote": {
                    "type": "object",
                    "required": ["target_class_id"],
                    "properties": {"target_class_id": {"type": "string"}},
                },
            }
        },
    }