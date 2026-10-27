# Sample Indian Sign Language (ISL) Vocabulary Entries

This directory contains **10 validated sample ISL vocabulary specifications in JSON format**.
You can import any of these entries directly into the Signify application via the **"Import Reviewed Vocabulary Entry"** modal in the UI or via the REST API (`POST /api/v1/signs/import`).

---

## 📂 Included Sample Signs

| File Name | Sign ID | English | Hindi (हिंदी) | Category | Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `01_welcome.json` | `isl_custom_welcome` | Welcome | स्वागत है / पधारिए | Greetings | Word |
| `02_tea_chai.json` | `isl_custom_tea` | Tea / Chai | चाय | Daily Living | Word |
| `03_medicine.json` | `isl_custom_medicine` | Medicine / Tablets | दवाई / औषधि | Medical / Emergency | Word |
| `04_sorry.json` | `isl_custom_sorry` | Sorry / Apology | माफ़ कीजिए | Courtesy | Word |
| `05_please.json` | `isl_custom_please` | Please | कृपया | Courtesy | Word |
| `06_stop.json` | `isl_custom_stop` | Stop / Halt | रुको / बंद करो | Emergency | Word |
| `07_nice_to_meet_you.json` | `isl_custom_nice_to_meet_you` | Nice to meet you | आपसे मिलकर खुशी हुई | Greetings | Phrase |
| `08_ambulance.json` | `isl_custom_ambulance` | Ambulance | एम्बुलेंस | Medical / Emergency | Word |
| `09_money.json` | `isl_custom_money` | Money / Cash | पैसे / रुपए | Daily Living | Word |
| `10_family.json` | `isl_custom_family` | Family | परिवार | Daily Living | Word |
| `batch_all_10_samples.json` | *(All 10)* | *(All 10)* | *(All 10)* | *(All categories)* | Array |

---

## 🚀 How to Import into Signify

### Option A: Using the Signify Web UI
1. Open the Signify Web App in your browser.
2. Sign in with Google (top right).
3. Navigate to the **"Supported Sign Dictionary"** tab.
4. Click the **"+ Import Entry"** button.
5. Open any `.json` file from this folder, copy its contents, paste it into the text box, and click **"Validate & Save"**.
6. The new sign will immediately be registered into the live SQLite dictionary database without modifying code!

### Option B: Batch Import All 10 Signs at Once
* Copy the contents of `batch_all_10_samples.json` and paste it into the Import modal. The frontend supports both single objects and JSON arrays of signs!
