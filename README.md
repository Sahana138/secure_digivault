# DigiVault: AI-Enabled Secure Digital Vault

A Flask web app that protects confidential files with **face recognition**, **blink-based liveness detection (anti-spoofing)**, **email OTP** and **Fernet encryption**, plus **intrusion monitoring** that locks accounts and sends alerts after repeated failed logins.


## Why this project

Passwords can be guessed, phished or brute-forced. Many face-login systems can be fooled by a photo of the user, and most file storage relies on access control rather than encryption. DigiVault combines authentication, anti-spoofing, encrypted storage and monitoring in one platform that runs on a normal laptop with a webcam.

## Features

- **Face authentication:** the user's face is encoded at registration and compared on every login (`face_recognition`, 128-D encodings).
- **Blink liveness detection:** a custom CNN classifies eye state (open/closed) from dlib eye landmarks. A closed-then-open sequence counts as a blink, so a static photo is rejected.
- **Email OTP:** a 6-digit, time-limited code is sent to the registered email over SMTP/TLS.
- **Encrypted vault:** files are encrypted with Fernet (AES-128-CBC + HMAC) before being written to disk. Upload, download, update and delete are supported.
- **Intrusion monitoring:** failed attempts are counted. After 3 failures the account is temporarily locked and a security alert email is sent.
- **Web UI:** responsive HTML/CSS/JS interface with Bootstrap.

## How login works

1. User enters their email.
2. Webcam captures a face, and it is matched against the stored encoding.
3. Blink check confirms a live person is present.
4. A 6-digit OTP is emailed and must be entered before it expires.
5. On success, the user reaches the encrypted vault. Any failure increases the failed-attempt count.

## Tech stack

| Area | Tools |
|---|---|
| Backend | Python 3.11, Flask, SQLAlchemy |
| Database | SQLite |
| Computer vision | OpenCV, dlib, face_recognition |
| Deep learning | TensorFlow / Keras (custom blink CNN) |
| Security | cryptography (Fernet), smtplib (SMTP/TLS), python-dotenv |
| Frontend | HTML, CSS, JavaScript, Bootstrap |

## Project structure

```
secure_digivault/
├── app.py                   # main Flask server and routes
├── modules/
│   ├── face_auth.py         # face encoding and verification
│   ├── anti_spoof.py        # blink liveness check (CNN + dlib landmarks)
│   ├── otp_service.py       # OTP generation and verification
│   ├── email_service.py     # OTP and security alert emails
│   └── vault_crypto.py      # Fernet encrypt / decrypt
├── database/
│   ├── db.py                # SQLAlchemy setup
│   └── models.py            # User model
├── templates/               # auth pages, home, vault dashboard
├── static/                  # CSS and images
├── blink_model.h5           # trained blink detection model
├── prepare_dataset.py       # dataset preparation for the blink model
├── train_blink_model.py     # CNN training script
├── evaluate_model.py        # model evaluation
├── requirements.txt
└── .env.example
```

## Getting started

### Prerequisites
- Python 3.11
- A webcam
- A Gmail account with an [app password](https://support.google.com/accounts/answer/185833) for sending OTP emails
- On Windows, `dlib` needs **CMake** and the **Visual Studio C++ build tools** to install

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/Sahana138/secure_digivault.git
   cd secure_digivault
   ```
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Linux / macOS
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Download dlib's **`shape_predictor_68_face_landmarks.dat`** (the standard 68-point face landmark model from the dlib website), unzip it, and place it in the project root. It is about 97 MB, so it is not included in this repo.
5. Copy `.env.example` to `.env` and fill in your values
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-gmail-app-password
   SECRET_KEY=a-long-random-string
   ```
6. Run the app
   ```bash
   python app.py
   ```
   Then open the URL shown in the terminal (usually `http://127.0.0.1:5000`).

The encryption key file `vault.key` is generated automatically on first run. **Back it up and never commit it:** without it, encrypted files cannot be decrypted.

## Blink detection model

- **Dataset:** MRL Eye Dataset plus additional public eye-state images, 16,981 images (8,390 open, 8,591 closed).
- **Preprocessing:** resize, greyscale, normalise to [0, 1], flip/rotate augmentation, noise filtering, eye-region extraction with dlib landmarks.
- **Results (eye-state classification):** accuracy 98.59%, FAR 1.11%, FRR 1.71%.

| Actual \ Predicted | Open | Closed |
|---|---|---|
| Open | 8,297 | 93 |
| Closed | 147 | 8,444 |

The dataset is not included in the repo. To retrain, download the MRL Eye Dataset, then use `prepare_dataset.py`, `train_blink_model.py` and `evaluate_model.py`.

## Testing

Unit, integration, system, validation and security test cases were run, covering registration, face match, blink detection, OTP validation and expiry, encryption/decryption, photo spoof rejection, invalid OTP, unauthorized vault access and account lockout. All passed. The average full authentication time (face, blink and OTP entry) was about 4 to 6 seconds.

## Security notes

- `.env`, `vault.key`, the face dataset, uploaded vault files and the user database are excluded from this repository.
- Facial encodings are stored in the database as serialized vectors, not images.
- Files are stored only in encrypted form, and are decrypted in memory when downloaded.

## Limitations

- Face recognition and blink detection degrade in poor lighting or with a low-quality webcam.
- Blink detection does not defend against advanced deepfake or video replay attacks.
- OTP delivery needs internet access and a working email service.
- SQLite suits small deployments but not large-scale use.

## Future work

Deepfake and replay detection, multimodal biometrics (fingerprint/iris), a PostgreSQL/MySQL backend, cloud storage, a mobile app, AI-based anomaly detection for intrusion monitoring, and an admin dashboard.