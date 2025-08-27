#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from json import dumps
import base64
from datetime import datetime
from epic_api_client.EPICClient import EPICHttpClient


class FHIRBase:

    def __init__(self, epic_client: EPICHttpClient) -> None:
        """
        Initialize the FHIRBase class.

        :param epic_client: The EPICClient instance to use for making requests.
        :type epic_client: EPICClient
        """
        self.epic_client = epic_client
        self.post = self.epic_client.post
        self.get = self.epic_client.get
        self.put = self.epic_client.put
        self.delete = self.epic_client.delete
        self.patch = self.epic_client.patch
        self.base_url = self.epic_client.base_url

    def get_metadata(self, version: str = "R4", verbose: bool = False) -> dict:
        """
        Retrieve metadata for a specified FHIR version.

        :param version: str, the FHIR version for which metadata is requested (options: 'DSTU2', 'STU3', 'R4').
        :return: dict, the response containing metadata from the FHIR server.
        """
        if version not in ["DSTU2", "STU3", "R4"]:
            raise ValueError(
                "Invalid version. Please specify either 'DSTU2', 'STU3' or 'R4'."
            )

        endpoint = f"/api/FHIR/{version}/metadata"
        response = self.get(endpoint)
        if verbose: 
            print("GET response:", response)

        return response

    def get_resource(
        self,
        resource_type: str,
        resource_id: str = None,
        version: str = "R4",
        **optional_params: dict,
    ) -> dict:
        """
        Get a FHIR resource with mandatory and optional parameters.

        :param resource_type: str, the type of the FHIR resource (e.g., 'Patient', 'Encounter')
        :param resource_id: str, the ID of the resource (optional)
        :param version: str, the FHIR version (default: 'R4')
        :param optional_params: dict, optional query parameters to be added to the URL

        :return: dict, the response from the FHIR server
        """
        base_url = f"api/FHIR/{version}/{resource_type}"

        if resource_id:
            base_url += f"/{resource_id}"

        qlist = []
        if optional_params:
            # Append optional query parameters to the qlist
            for key, value in optional_params.items():
                if value is not None:
                    qlist.append(f"{key}={value}")

        query_string = "&".join(qlist)
        url = f"{base_url}?{query_string}" if qlist else base_url

        return self.get(url)

    def post_resource(
        self,
        resource_type: str,
        request_body: dict,
        version: str = "R4",
        **optional_params: dict,
    ) -> dict:
        """
        Post a FHIR resource with a mandatory JSON body and optional parameters.

        :param resource_type: str, the type of the FHIR resource (e.g., 'Patient', 'Encounter')
        :param request_body: dict, the JSON body to be posted
        :param version: str, the FHIR version (default: 'R4')
        :param optional_params: dict, optional query parameters to be added to the URL

        :return: dict, the response from the FHIR server
        """
        base_url = f"api/FHIR/{version}/{resource_type}"

        if optional_params:
            # Append optional query parameters to the URL
            qlist = [
                f"{key}={value}"
                for key, value in optional_params.items()
                if value is not None
            ]
            query_string = "&".join(qlist)
            url = f"{base_url}?{query_string}"
        else:
            url = base_url

        return self.post(url, json=request_body)

    def patient_read(self, patient_id: str) -> dict:
        """
        Retrieve patient information by patient ID.

        :param patient_id: str, the ID of the patient
        :return: dict, the response from the FHIR server
        """
        return self.get_resource("Patient", patient_id)

    def patient_search(
        self,
        address: str = None,
        address_city: str = None,
        address_postalcode: str = None,
        address_state: str = None,
        birthdate: str = None,
        family: str = None,
        gender: str = None,
        given: str = None,
        identifier: str = None,
        name: str = None,
        own_name: str = None,
        own_prefix: str = None,
        partner_name: str = None,
        partner_prefix: str = None,
        telecom: str = None,
        legal_sex: str = None,
        active: bool = None,
        address_use: str = None,
        death_date: str = None,
        email: str = None,
        general_practitioner: str = None,
        language: str = None,
        link: str = None,
        organization: str = None,
        phone: str = None,
        phonetic: str = None,
    ) -> dict:
        """
        Search for patients using a variety of parameters.

        :param address: Optional[str], the address of the patient
        :param address_city: Optional[str], the city of the patient's address
        :param address_postalcode: Optional[str], the postal code of the patient's address
        :param address_state: Optional[str], the state of the patient's address
        :param birthdate: Optional[str], the birthdate of the patient
        :param family: Optional[str], the family name of the patient
        :param gender: Optional[str], the gender of the patient
        :param given: Optional[str], the given name of the patient
        :param identifier: Optional[str], the identifier for the patient
        :param name: Optional[str], the full name of the patient
        :param own_name: Optional[str], the patient's own name
        :param own_prefix: Optional[str], the prefix for the patient's own name
        :param partner_name: Optional[str], the name of the patient's partner
        :param partner_prefix: Optional[str], the prefix for the patient's partner's name
        :param telecom: Optional[str], the telecom information for the patient
        :param legal_sex: Optional[str], the legal sex of the patient
        :param active: Optional[bool], whether the patient is active
        :param address_use: Optional[str], the use of the address
        :param death_date: Optional[str], the death date of the patient
        :param email: Optional[str], the email of the patient
        :param general_practitioner: Optional[str], the general practitioner of the patient
        :param language: Optional[str], the language of the patient
        :param link: Optional[str], the link to related patient information
        :param organization: Optional[str], the organization related to the patient
        :param phone: Optional[str], the phone number of the patient
        :param phonetic: Optional[str], the phonetic spelling of the patient's name

        :return: dict, the response from the FHIR server
        """
        # Build query parameters
        params = {
            "address": address,
            "address-city": address_city,
            "address-postalcode": address_postalcode,
            "address-state": address_state,
            "birthdate": birthdate,
            "family": family,
            "gender": gender,
            "given": given,
            "identifier": identifier,
            "name": name,
            "own-name": own_name,
            "own-prefix": own_prefix,
            "partner-name": partner_name,
            "partner-prefix": partner_prefix,
            "telecom": telecom,
            "legal-sex": legal_sex,
            "active": active,
            "address-use": address_use,
            "death-date": death_date,
            "email": email,
            "general-practitioner": general_practitioner,
            "language": language,
            "link": link,
            "organization": organization,
            "phone": phone,
            "phonetic": phonetic,
        }

        # Remove any parameters that are None (not provided)
        params = {key: value for key, value in params.items() if value is not None}

        # Send GET request with the constructed parameters
        return self.get_resource("Patient", params=params)

    def encounter_read(self, encounter_id: str) -> dict:
        """
        Retrieve encounter information by patient ID.

        :param encounter_id: str, the ID of the encounter
        :return: dict, the response from the FHIR server
        """
        return self.get_resource("Encounter", encounter_id)

    def encounter_search(self, patient_id: str) -> dict:
        """
        Retrieve encounters by patient ID.

        :param patient_id: str, the ID of the patient
        :return: dict, the response from the FHIR server
        """
        return self.get_resource("Encounter", patient=patient_id)

    def document_reference_read(self, document_reference_id: str) -> dict:
        """
        Retrieve document_reference information by document_reference_id.

        :param document_reference_id: str, the ID of the document reference
        :return: dict, the response from the FHIR server
        """
        return self.get_resource("DocumentReference", document_reference_id)

    def document_reference_search(
        self,
        category: str = None,
        date: str = None,
        docstatus: str = None,
        encounter: str = None,
        patient: str = None,
        period: str = None,
        subject: str = None,
        d_type: str = None,
    ) -> dict:
        """
        Retrieve document references using various search parameters.

        :param category: Optional[str], the category of the document reference
        :param date: Optional[str], the date of the document reference
        :param docstatus: Optional[str], the status of the document
        :param encounter: Optional[str], the encounter associated with the document
        :param patient: Optional[str], the patient ID associated with the document
        :param period: Optional[str], the period during which the document was created
        :param subject: Optional[str], the subject associated with the document (e.g., patient or group)
        :param d_type: Optional[str], the type of the document

        :return: dict, the response from the FHIR server containing the document references
        """
        if not (subject or patient):
            raise ValueError("At least one of subject or patient must be provided")
        if not (category or d_type):
            category = "clinical-note"
        return self.get_resource(
            "DocumentReference",
            category=category,
            date=date,
            docstatus=docstatus,
            encounter=encounter,
            patient=patient,
            period=period,
            subject=subject,
            type=d_type,
        )

    def observation_create(
        self,
        patient_id: str,
        encounter_id: str,
        flowsheet_id: str,
        name: str,
        value: float,
    ) -> dict:
        """Create observation. For now only 1 entry per call is supported

        :param patient_id: str, the ID of the patient
        :param encounter_id: str, the ID of the encounter
        :param flowsheet_id: str, the ID of the flowsheet
        :param name: str, the name of the observation
        :param value: float, the value of the observation
        :return: dict, the response from the FHIR server
        """
        url = "/api/FHIR/R4/Observation"
        observation = {
            "resourceType": "Observation",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }
                    ],
                    "text": "Vital Signs",
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://open.epic.com/FHIR/StructureDefinition/observation-flowsheet-id",  # urn:oid:2.16.840.1.113883.6.88
                        "code": flowsheet_id,
                        "display": name,
                    }
                ],
                "text": name,
            },
            "subject": {
                "reference": "Patient/" + patient_id,
                # "display": "Meiko Lufhir"
            },
            "encounter": {"reference": "Encounter/" + encounter_id},
            "effectiveDateTime": datetime.utcnow().strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),  # "2019-09-05T20:00:00Z",
            "valueQuantity": {
                "value": value,
                # "unit": "",
                # "system": "http://unitsofmeasure.org",
                # "code": "%"
            },
            "status": "final",
        }
        return self.post(url, json=observation)

    def document_reference_create(
        self,
        patient_id: str,
        encounter_id: str,
        note_text: str,
        note_type: str = "Consultation Note",
        doc_status: str = "final",
        prefer: str = "return=representation",
    ) -> dict:
        """
        Create a DocumentReference resource in the FHIR server.

        :param patient_id: str, the ID of the patient
        :param encounter_id: str, the ID of the encounter
        :param note_text: str, the plain text of the note
        :param note_type: str, the type of the note, default is "Consultation Note"
        :param doc_status: str, the status of the document, default is "final"
        :param prefer: str, the prefer header to control the response, default is "return=representation"

        :return: dict, the response from the FHIR server
        """
        url = "/api/FHIR/R4/DocumentReference"
        headers = {"Content-Type": "application/fhir+json", "Prefer": prefer}

        document_reference = {
            "resourceType": "DocumentReference",
            "docStatus": doc_status,
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11488-4",
                        "display": note_type,
                    }
                ],
                "text": note_type,
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "content": [
                {
                    "attachment": {
                        "contentType": "text/plain",
                        "data": base64.b64encode(note_text.encode("utf-8")).decode(
                            "utf-8"
                        ),
                    }
                }
            ],
            "context": {"encounter": [{"reference": f"Encounter/{encounter_id}"}]},
        }

        return self.post(url, extra_headers=headers, data=dumps(document_reference))

    def condition_read(self, condition_id: str) -> dict:
        """
        Retrieve a single condition from a patient's chart by ID.

        Args:
            condition_id (str): FHIR identifier for the target Condition resource.

        Returns:
            dict: The JSON response containing the condition resource.
        """
        return self.get_resource("Condition", condition_id)

    def condition_search(
        self,
        patient: str,
        clinical_status: str = None,
        category: str = "problem-list-item",
        **optional_params: dict,
    ) -> dict:
        """
        Search for Condition resources in a patient's chart.

        :param patient: str, the patient ID (mandatory)
        :param clinical_status: str, the clinical status of the condition (e.g., 'active', 'resolved', 'inactive') (optional)
        :param category: str, the category of the condition (default: 'problem-list-item') (optional)
        :param optional_params: dict, additional query parameters for filtering (optional)

        :return: dict, the response from the FHIR server
        """
        if not patient:
            raise ValueError("The 'patient' parameter is required.")

        # Mandatory query parameters
        query_params = {
            "patient": patient,
            "category": category,
        }

        # Add optional clinical status if provided
        if clinical_status:
            query_params["clinical-status"] = clinical_status

        # Include any additional optional parameters
        for key, value in optional_params.items():
            if value is not None:
                query_params[key] = value

        # Build the URL with query parameters
        return self.get_resource("Condition", **query_params)

    def condition_create(self, json_body: dict) -> dict:
        """
        Create a Condition resource in the FHIR server.

        :param json_body: dict, the JSON body of the Condition resource

        :return: dict, the response from the FHIR server
        """
        return self.post_resource("Condition", json_body)
