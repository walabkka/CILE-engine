# Clinical Informatics Logic Engine (CILE) v1.0.0

CILE is a deterministic clinical decision support (CDS) tool for real-time safety interception and population-specific pharmacology. It transforms fragmented drug safety data into deterministic, interoperable HL7 FHIR output prioritizing high-alert intercepts and pharmacogenomic risks for real-time clinical decision support.

## Project Overview NABC:
* **Need:** Clinical safety data is often fragmented across regulatory databases (FDA), specialized guidelines (Beers Criteria), and genomic resources. Manually cross-referencing these leads to high cognitive load and potential human error.
* **Approach:** CILE utilizes a distributed, cloud-based architecture. A multi-layered extraction process that normalizes medication names via RxNorm and the OpenFDA API that filters through proprietary logic gates and user's input.
* **Benefit:** Provides clinicians and technicians with a consolidated safety profile including population-specific intercepts, dynamic renal adjustments, and pharmacogenomic (PGx) markers—outputting both physical PDF Consultation Reports and machine-readable HL7 FHIR payloads.
* **Competition:** Unlike static PDF references or broad consumer-facing databases, CILE provides a real-time, logic-driven fallback system that prioritizes high-alert clinical intercepts over generic metadata.  

####*Note: This system has been evaluated using the STARE-HI (Statement on Reporting of Evaluation Studies in Health Informatics) framework. Detailed evaluation of the system architecture and clinical problem context can be found in `evaluation_log.md`. The clinical logic and architecture were self-directed. AI was utilized as a pair-programmer" to navigate API structures and refine Python syntax, allowing the primary focus to remain on healthcare informatics and data behavior. Prompt engineering skills are required!*
----------------------------------------
## Built With
* **Engine:** Python 3.14+, FastAPI, SQLAlchemy, PostgreSQL
* **Client Interface:** Streamlit, Pandas, FPDF2
* **Sources:**
  * **RxNorm (NLM):** For terminology standards and RxCUI mapping.
  * **openFDA:** Used for Boxed Warnings, Adverse Events, and Pharmacogenomic (PGx) markers.
  * **RxNav Interaction API (NLM):** It gets interactions between drug products.
  * **RxClass (NLM):** Used for therapeutic class mapping.
* **Evaluation Framework:** **STARE-HI** *(Statement on Reporting of Evaluation Studies in Health Informatics)*

## Deployment Workflow
The core calculation engine and clinical intercepts are on a private backend. Contact CILE's builder for more. Otherwise to run CILE locally:
1) Clone this repository:
   ```bash
   git clone https://github.com/walabkka/CILE-engine.git
   cd CILE-engine
2) pip install -r requirements.txt