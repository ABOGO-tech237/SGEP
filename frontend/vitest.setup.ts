import "@testing-library/jest-dom";

process.env.JWT_SECRET = "test-jwt-secret-at-least-32-chars!!";
process.env.DJANGO_API_URL = "http://localhost:8000";
