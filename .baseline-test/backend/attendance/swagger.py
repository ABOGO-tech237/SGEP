from __future__ import annotations


def build_attendance_openapi_schema() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "SGEP Attendance API",
            "version": "1.0.0",
            "description": "Documentation Swagger du module presence simplifie, reserve au SuperAdmin.",
        },
        "security": [{"bearerAuth": []}],
        "paths": {
            "/api/v1/attendance/": {
                "get": {
                    "summary": "Lister les enregistrements de presence",
                    "tags": ["Attendance"],
                    "operationId": "listAttendanceRecords",
                    "parameters": [
                        {"name": "class_id", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "student_id", "in": "query", "required": False, "schema": {"type": "string"}},
                        {"name": "date_from", "in": "query", "required": False, "schema": {"type": "string", "format": "date"}},
                        {"name": "date_to", "in": "query", "required": False, "schema": {"type": "string", "format": "date"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "Liste des enregistrements.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AttendanceListResponse"}
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Enregistrer une absence ou un retard",
                    "tags": ["Attendance"],
                    "operationId": "createAttendanceRecord",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AttendanceCreate"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Enregistrement cree.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Attendance"}
                                }
                            },
                        }
                    },
                },
            },
            "/api/v1/attendance/{record_id}/": {
                "put": {
                    "summary": "Mettre a jour un enregistrement",
                    "tags": ["Attendance"],
                    "operationId": "updateAttendanceRecord",
                    "parameters": [
                        {"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AttendanceUpdate"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Enregistrement mis a jour.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Attendance"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/attendance/{record_id}/justify/": {
                "post": {
                    "summary": "Justifier une absence",
                    "tags": ["Attendance"],
                    "operationId": "justifyAttendanceRecord",
                    "parameters": [
                        {"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AttendanceJustify"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Absence justifiee.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Attendance"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/attendance/stats/": {
                "get": {
                    "summary": "Statistiques de presence",
                    "tags": ["Attendance"],
                    "operationId": "getAttendanceStats",
                    "parameters": [
                        {"name": "class_id", "in": "query", "required": True, "schema": {"type": "string"}},
                        {"name": "date_from", "in": "query", "required": True, "schema": {"type": "string", "format": "date"}},
                        {"name": "date_to", "in": "query", "required": True, "schema": {"type": "string", "format": "date"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "Statistiques par eleve.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AttendanceStatsResponse"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/attendance/export/": {
                "get": {
                    "summary": "Exporter la presence en PDF ou Excel",
                    "tags": ["Attendance"],
                    "operationId": "exportAttendance",
                    "parameters": [
                        {"name": "class_id", "in": "query", "required": True, "schema": {"type": "string"}},
                        {"name": "date_from", "in": "query", "required": True, "schema": {"type": "string", "format": "date"}},
                        {"name": "date_to", "in": "query", "required": True, "schema": {"type": "string", "format": "date"}},
                        {"name": "format", "in": "query", "required": True, "schema": {"type": "string", "enum": ["pdf", "excel"]}},
                    ],
                    "responses": {
                        "202": {
                            "description": "Export lance.",
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
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            },
            "schemas": {
                "Attendance": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "student_id": {"type": "string"},
                        "class_id": {"type": "string"},
                        "date": {"type": "string", "format": "date"},
                        "type": {"type": "string", "enum": ["absence", "retard"]},
                        "motif": {"type": "string", "nullable": True},
                        "is_justified": {"type": "boolean"},
                        "justification_motif": {"type": "string", "nullable": True},
                        "justification_doc": {"type": "string", "nullable": True},
                    },
                },
                "AttendanceCreate": {
                    "type": "object",
                    "required": ["student_id", "class_id", "date", "type"],
                    "properties": {
                        "student_id": {"type": "string"},
                        "class_id": {"type": "string"},
                        "date": {"type": "string", "format": "date"},
                        "type": {"type": "string", "enum": ["absence", "retard"]},
                        "motif": {"type": "string", "nullable": True},
                    },
                },
                "AttendanceUpdate": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "format": "date"},
                        "type": {"type": "string", "enum": ["absence", "retard"]},
                        "motif": {"type": "string", "nullable": True},
                    },
                },
                "AttendanceJustify": {
                    "type": "object",
                    "required": ["motif"],
                    "properties": {
                        "motif": {"type": "string"},
                        "justification_doc": {"type": "string", "nullable": True},
                    },
                },
                "AttendanceListResponse": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Attendance"},
                        },
                    },
                },
                "AttendanceStatsResponse": {
                    "type": "object",
                    "properties": {
                        "class_id": {"type": "string"},
                        "date_from": {"type": "string", "format": "date"},
                        "date_to": {"type": "string", "format": "date"},
                        "working_days": {"type": "integer"},
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "student_id": {"type": "string"},
                                    "absences": {"type": "integer"},
                                    "retards": {"type": "integer"},
                                    "justified_absences": {"type": "integer"},
                                    "absence_rate": {"type": "number"},
                                },
                            },
                        },
                    },
                },
                "ExportJobResponse": {
                    "type": "object",
                    "properties": {"job_id": {"type": "string"}},
                },
            },
        },
    }