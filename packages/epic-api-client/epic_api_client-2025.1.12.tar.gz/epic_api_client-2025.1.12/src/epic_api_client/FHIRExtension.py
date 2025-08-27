#    ____   # -------------------------------------------------- #
#   | ^  |  # EPICClient for AUMC               				 #
#   \  --   # o.m.vandermeer@amsterdamumc.nl        			 #
# \_| ﬤ| ﬤ  # If you like this code, treat him to a coffee! ;)	 #
#   |_)_)   # -------------------------------------------------- #

from .FHIRBase import FHIRBase


class FHIRExtension(FHIRBase):
    def patient_search_MRN(self, ID_type: str, patient_mrn: str) -> dict:
        """Retrieve patient information by patient MRN."""
        mrn_id = ID_type + "|" + patient_mrn
        return self.patient_search(identifier=mrn_id)

    def mrn_to_FHIRid(self, patient_mrn: str) -> str:
        result = self.patient_search_MRN(ID_type="MRN", patient_mrn=patient_mrn)
        if len(result["entry"]) == 0:
            raise ValueError("Patient not found: ", patient_mrn)
        FHIRid = result["entry"][0]["resource"]["id"]
        return FHIRid
