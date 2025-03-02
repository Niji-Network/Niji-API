# API Documentation Guide

This document explains how to maintain and update the API documentation for the Niji API.

---

## Overview

The Niji API documentation is automatically generated from the code using FastAPI’s OpenAPI integration. The schema is exported as a YAML file at `/docs/openapi.yaml`, and interactive documentation is available via ReDoc at `/docs`.

---

## How to Update Documentation

1. **Update Inline Docstrings:**  
   - Modify or add docstrings and inline comments in your FastAPI routes, models, and utilities.
   - Follow FastAPI’s [documentation conventions](https://fastapi.tiangolo.com/tutorial/) to ensure that the OpenAPI schema is generated correctly.

2. **Generate the OpenAPI Schema:**  
   - Run the application locally.
   - The custom OpenAPI generation function (in `main.py`) automatically writes the schema to `/docs/openapi.yaml`.
   - Verify that the YAML file reflects your updates.

3. **Verify with Interactive Docs:**  
   - Open your browser and navigate to `http://localhost:5000/docs` (or the appropriate URL for your deployment).
   - Use ReDoc to review the interactive documentation and confirm that endpoints, parameters, and response examples are correct.

4. **Submit Your Changes:**  
   - Once you are satisfied with the updates, commit the changes (including the regenerated `/docs/openapi.yaml` file).
   - Open a Pull Request to merge your documentation improvements.

---

## Best Practices

- **Consistency:** Ensure consistent formatting and style in your docstrings for clarity.
- **Examples:** Provide clear examples in your docstrings (using triple backticks for code blocks) so that response schemas and parameter usage are easy to understand.
- **Testing:** Test the generated documentation locally to catch any issues before submitting your changes.

---

## Contributing to the Docs

Wanna update something on docs? Open a PR!

If you have questions or suggestions about the documentation, please open an issue or contact one of the maintainers.

---

Happy documenting!
