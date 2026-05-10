# Clinical Informatics Logic Engine (CILE) v1.0.0

CILE is a deterministic clinical decision support (CDS) tool for real-time safety intercept, population-specific pharmacology. It transforms fragmented drug safety data into a deterministic, interoperable HL7 FHIR output prioritizing high-alert intercepts and pharmacogenomic risks for real-time clinical decision support.

## Project Overview NABC:
* Need: Clinical safety data is often fragmented across regulatory databases (FDA), specialized guidelines (Beers Criteria), and genomic resources. Manually cross-referencing these leads to high cognitive load and potential human error.
* Approach: CILE utilizes a distributed, cloud-based architecture. A secure backend engine normalizes medication names via RxNorm and executes a multi-layered extraction process using the OpenFDA API and proprietary logic gates. This repository contains the Streamlit Client interface.
* Benefit: Provides clinicians and technicians with a consolidated safety profile including population-specific intercepts, dynamic renal adjustments, and pharmacogenomic (PGx) markers—outputting both physical PDF Consultation Reports and machine-readable HL7 FHIR payloads.
* Competition: Unlike static PDF references or broad consumer-facing databases, CILE provides a real-time, logic-driven fallback system that prioritizes high-alert clinical intercepts over generic metadata.  

*Note: This system has been evaluated using the STARE-HI (Statement on Reporting of Evaluation Studies in Health Informatics) framework. Detailed evaluation of the system architecture and clinical problem context can be found in `evaluation_log.md`.*
----------------------------------------
## Clinical Logic & Architecture
CILE follows a deterministic architecture. It converts raw user input to a normalized RxNorm concept ID before querying the OpenFDA discovery API. This ensures that safety intercepts are triggered by the chemical moiety rather than inconsistent brand naming.
The logic is processed through five primary layers:
* **Population Intercepts:** A localized JSON database that intercepts queries to flag high-risk scenarios for special populations.
* **Drug Classification:** Categorize the medication to local safety tags (e.g., [OTC], [RX], [HIGH-ALERT], [NARCOTIC]).
* **Route Organization (RoA):** Organizes and filters FDA metadata by route of administration ([Oral], [IV], [SubQ]) to ensure clinical relevance to the prescribed regimen.
* **Bio-Molecular Analysis (PGx):** Active scanning of FDA metadata using regex patterns for pharmacogenomic (PGx) markers (e.g., [CYP2C19], [CYP3A4], [HLA-B*1502]) to flag gene-drug interaction risks.
* **FDA Safety Extraction:** Retrieves the most critical safety information using a prioritized hierarchy: Boxed Warning → Warnings & Precautions → Precautions.

## Key Features
* **Standardized Normalization:** Integrated RxNorm that translates proprietary brand names into clinical terms, ensuring the FDA database queries the correct active ingredient.
* **Population Intercepts:** Deterministic catch for the high-risk scenarios for Geriatric (Beers Criteria), Pediatric, Pregnancy, and Renal populations.
* **Bio-Molecular Analysis:** Beyond standard scanning, CILE utilizes regex patterns to detect pharmacogenomic (PGx) markers to flag gene-drug interaction risks, including HLA-alleles, Retinoid Receptors, and Teratogenic vectors found within FDA metadata.
* **Relational DDI Analysis:** Two-tier interaction checking using a localized priority matrix and the Global NLM RxNav API.
* **Safety Extraction:** Automated retrieval of Boxed Warnings and Precautions directly from OpenFDA data source and extraction of fallback loop to eliminate data gaps in raw FDA metadata. Plus it automatically flags medications that might have genetic risks, helping providers make safer choices.
* **Interoperable Export:** Generation of HL7 FHIR-standardized JSON document (DetectedIssue Resource) or PDF Report to facilitate clinical data exchange.

## Built With
* **Engine:** Python 3.14.4+, FastAPI, SQLAlchemy, PostgreSQL
* **Client Interface:** Streamlit, Pandas, FPDF2
* **Sources:** * **OpenFDA:** For live clinical and regulatory data.
  * **RxNorm (NLM):** For terminology standards and RxCUI mapping.
  * **RxNav Interaction API (NLM):** It gets interactions between drug products.
  * **openFDA:** Used for Boxed Warnings, Adverse Events, and Pharmacogenomic (PGx) markers.
  * **RxClass (NLM):** Used for therapeutic class mapping.
* **Frameworks:** *STARE-HI (Statement on Reporting of Evaluation Studies in Health Informatics)*

## Deployment Workflow
The core calculation engine and clinical intercepts are on a private backend. To evaluate the client workstation locally:
1.  Clone this repository cd git clone https://github.com/walabkka/CILE-engine
2.  Install requirements: `pip install -r requirements.txt`
3.  Configure Streamlit secrets (`.streamlit/secrets.toml`) with the designated API keys.
4.  Launch the UI: `streamlit run cile_ui.py`