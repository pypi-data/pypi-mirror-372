# EPIC API Client
If your favorite function is not yet implemented, let me know, I will do this for you!

## Installation

use pip install EPIC-API-Client.<br/>
see example.py for usage and setup .env accordingly.<br/>
tip: use uv pip for faster pip (`pip install uv`)!<br/>

## How to use

### Testing on EPIC sandbox
To familiarize, play around and test out the functionality of this package, you can use the EPIC sandbox. To use this sandbox, you only need to register an app at vendor services of EPIC, enable the EPIC sandbox and you're done! In the environment file, use the url of the EPIC sandbox for your organisation.

### Using this wrapper within Nebula
Nebula uses unix websockets to send web requests instead of simple http requests. This capability has been added to this wrapper which can be activated setting the use_unix_socket=True argument:<br/>
`client = EPICClient(client_id=client_id, jwt_generator=jwt_generator, base_url=base_url, use_unix_socket=True)`<br/>
Make sure to setup your Nebula environment as if you would use the Webcallout functionality from EPIC itself.<br/>

### 1. Using FHIR API functions

This wrapper provides a convenient way to interact with EPIC's FHIR APIs. All FHIR-related functions are accessible through the `fhir` attribute of an initialized `EPICClient` instance.

For example, to read a patient resource:
```python
client = EPICClient(...) # Initialize as shown in example_public.py
client.obtain_access_token()
patient_data = client.fhir.patient_read(patient_id="some_patient_fhir_id")
client.print_json(patient_data)
```

The client supports common FHIR operations such as `read`, `search`, and `create` for various resources including Patient, Encounter, DocumentReference, Observation, and Condition. A comprehensive list of implemented FHIR functions can be found in the "Implemented functions" section below.

These functions are organized into:
*   **Base FHIR Functions**: Direct interactions with FHIR resources (e.g., `patient_read`, `encounter_search`) provided by the `FHIRBase` class.
*   **FHIR Extension Functions**: Higher-level convenience functions (e.g., `patient_search_MRN`, `mrn_to_FHIRid`) built upon the base functions, provided by the `FHIRExtension` class.

### 2. Authentication Methods

The client exclusively uses **OAuth 2.0 with JWTs (JSON Web Tokens)** for authentication, employing the client credentials grant type.

**Setup and Usage:**
1.  Initialize a `JWTGenerator` instance, providing the path to your PFX file and its password. You may also need to provide your `kid` (Key ID).
    ```python
    from epic_api_client import JWTGenerator
    jwt_generator = JWTGenerator(pfx_file_path="path/to/your.pfx", pfx_password="your_pfx_password", kid="your_key_id")
    ```
2.  Pass this `jwt_generator` along with your `client_id` and the `base_url` for the EPIC environment when creating an `EPICClient` instance.
3.  After initializing the client, you **must** call the `obtain_access_token()` method. This method uses the JWT to request an access token from EPIC's OAuth 2.0 token endpoint.
    ```python
    client = EPICClient(client_id="your_client_id", jwt_generator=jwt_generator, base_url="your_epic_base_url")
    client.obtain_access_token()
    ```
4.  Once `obtain_access_token()` is successful, the client will automatically include the access token in the headers for all subsequent API calls.

Currently, "basic token" authentication or other methods are **not** supported by this client.

### 3. How this wrapper is organized and what are base vs extensions?

The `EPIC-API-Client` is designed with a modular and extensible architecture:

*   **`EPICClient`**: This is the main class you interact with. It serves as the primary entry point and orchestrates the different components. It inherits from `EPICHttpClient`.

*   **`EPICHttpClient`**: This class handles the underlying HTTP communication, including sending requests and processing responses. It manages the OAuth 2.0 authentication flow (obtaining and using access tokens) and also supports using Unix domain sockets for integration with environments like Nebula (via the `use_unix_socket=True` parameter).

*   **Functional Modules (Base and Extensions)**:
    *   **FHIR Module**:
        *   **`FHIRBase`**: This class provides the foundational methods for interacting directly with FHIR resources. It implements generic functions like `get_resource` and `post_resource`, as well as specific methods for common FHIR operations (e.g., `patient_read`, `condition_create`).
        *   **`FHIRExtension`**: This class inherits from `FHIRBase` and builds upon its functionalities by adding higher-level, more specialized, or convenience functions related to FHIR. Examples include `patient_search_MRN` (searching a patient by MRN) and `mrn_to_FHIRid` (converting an MRN to a FHIR ID). These are accessed via `client.fhir`.

    *   **Internal API Module (Optional Extension)**:
        *   This functionality is provided by a separate package, `epic_internal_extension`, which can be installed if needed.
        *   **`InternalBase`**: Similar to `FHIRBase`, this class provides foundational methods for interacting with specific internal (non-FHIR) Epic APIs, such as those for SmartData elements or the Epic Cognitive Computing Platform (ECCP).
        *   **`InternalExtension`**: This class inherits from `InternalBase` and is intended to provide more specialized or composite functions for these internal Epic APIs. If the `epic_internal_extension` package is installed, these functions are accessible via `client.internal`.

In summary, the "base" classes (`FHIRBase`, `InternalBase`) offer core, direct API interaction capabilities. The "extension" classes (`FHIRExtension`, `InternalExtension`) inherit from their respective base classes to provide more advanced, specific, or user-friendly functionalities, making the client more powerful and easier to use for common tasks.

## Troubleshooting
- To print full requests and response for debugging purposes, initialise the client with `debug_mode=True`.<br/>
- AttributeError: module 'jwt' object has no attribute 'encode'<br/>
    ```
    uv pip uninstall jwt
    uv pip uninstall PyJWT
    uv pip install PyJWT
    ```

## Implemented functions

- FHIR API functions
    - get_metadata
    - patient_read
    - patient_search
    - encounter_read
    - encounter_search
    - document_reference_read
    - document_reference_search
    - document_reference_create
    - observation_create
    - condition_read
    - condition_search
    - condition_create
- FHIR API extention functions
    - patient_search_MRN
    - mrn_to_FHIRid

