# vmx-aps - APS command line wrapper

`vmx-aps` is a command-line utility for interacting with the [Verimatrix App Shield](https://www.verimatrix.com/cybersecurity/xtd-protect/) API. It simplifies operations like uploading apps, checking versions, and managing protections using a simple CLI.

---

## What's new in 2.6.0

- Added commands to handle signing certificates
- Added commands to set (and delete) protection configuration for applications and builds
- Added commands to set (get and delete) certificate pinning configuration for applications and builds
- Added optional parameters to the "protect" command:
  - --secondary-signing-certificate
  - --build-protection-configuration
  - --build-certificate-pinning-configuration

---

## 🛠️ Installation

```bash
$ pip install vmx-aps
```

---

## 🚀 Usage

All commands require an API key file (JSON format) obtained from the Verimatrix portal -> Settings -> API Key Manager.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json <command> [args...]
```

Example:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get_version
{
  "apkdefender": {
    "preanalysis-defaults": "20250401.json",
    "raven-apkdefender": "v4.8.3_20250401",
    "raven-template": "20250401.json",
    "sail": "1.46.4",
    "version": "4.8.3"
  },
  "apsdefenders": "2025.12.3-prod",
  "iosdefender": {
    "sail": "1.46.4",
    "version": "7.2.1"
  },
  "version": "2025.12.0-prod"
}
```

---

## 🔐 Authentication

All requests are authenticated via an API key in a local JSON file. The file must contain:

```json
{
  "appClientId": "your-app-client-id",
  "appClientSecret": "your-app-client-secret",
  "encodedKey": "your-encoded-key"
}
```

The CLI tool reads only the value of `encodedKey`. You can also pass that value as an argument directly using `--api-key` or `-a`:

```bash
$ vmx-aps -a "your-encoded-key" get_version
{
  "apkdefender": {
    "preanalysis-defaults": "20250401.json",
    "raven-apkdefender": "v4.8.3_20250401",
    "raven-template": "20250401.json",
    "sail": "1.46.4",
    "version": "4.8.3"
  },
  "apsdefenders": "2025.12.3-prod",
  "iosdefender": {
    "sail": "1.46.4",
    "version": "7.2.1"
  },
  "version": "2025.12.0-prod"
}
```

---

## 📚 Available Commands

### `protect`

Performs app protection on a given mobile app binary (Android or iOS). This is a high-level command that uploads an app, runs protection, waits for completion, and downloads the protected binary.

⚠️ This process may take **several minutes** to complete.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect --file path/to/app.apk
```

#### 🔧 Options

- `--file` **(required)**  
  Path to the input binary. Supported formats:

  - Android: `.apk`, `.aab`
  - iOS: zipped `.xcarchive` folder

- `--subscription-type` _(optional)_  
  Specifies the subscription type.  
  Choices: `["APPSHIELD_PLATFORM", "COUNTERSPY_PLATFORM", "XTD_PLATFORM"]`

- `--signing-certificate` _(optional)_  
  Path to a PEM-encoded signing certificate file, used for Android signature verification or certificate pinning.
  **NOTE**: this is mandatory for Android protection.

- `--secondary-signing-certificate` _(optional)_  
  Path to a PEM-encoded secondary signing certificate file, used for Android signature verification or certificate pinning.

- `--mapping-file` _(optional)_  
  Path to the Android R8/ProGuard mapping file for symbol preservation during obfuscation.

- `--build-protection-configuration` _(optional)_  
  Path to the build protection configuration JSON file.

- `--build-certificate-pinning-configuration` _(optional)_  
  Path to the JSON file with the build certificate pinning configuration.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect \
  --file ~/test-app.apk \
  --subscription-type XTD_PLATFORM \
  --signing-certificate ~/cert.pem \
  --secondary-signing-certificate ~/secondary-cert.pem \
  --mapping-file ~/proguard.map \
  --build-protection-configuration ~/buildProtConfig.json \
  --build-certificate-pinning-configuration ~/certPinningConfig.json
```

---

### `list-applications`

Lists applications associated with your Verimatrix App Shield account. You can filter the results by application ID, group, or subscription type.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-applications
```

#### 🔧 Options

- `--application-id` _(optional)_  
  If provided, returns details for a specific application matching the given ID.

- `--group` _(optional)_  
  Filters applications to those belonging to the specified group.

- `--subscription-type` _(optional)_  
  Specifies the subscription type.  
  Choices: `["APPSHIELD_PLATFORM", "COUNTERSPY_PLATFORM", "XTD_PLATFORM"]`

#### ✅ Examples

List all applications:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-applications
```

List a specific application:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-applications --application-id c034f8be-b41d-4799-ab3b-e96f2e60c2ae
```

List applications from a group:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-applications --group my-group
```

List applications with a specific subscription type:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-applications --subscription-type XTD_PLATFORM
```

---

### `add-application`

Registers a new application with Verimatrix App Shield. You must specify the platform, application name, and package ID. You can also set access restrictions and grouping options.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json add-application --os android --name "My App" --package-id com.example.myapp
```

#### 🔧 Options

- `--os` **(required)**  
  Target operating system.  
  Choices: `android`, `ios`

- `--name` **(required)**  
  Friendly display name for the application.

- `--package-id` **(required)**  
  The app's unique package ID (e.g., `com.example.myapp`).

- `--group` _(optional)_  
  Application group identifier, useful for managing related apps.

- `--subscription-type` _(optional)_  
  Specifies the subscription type.  
  Choices: `["APPSHIELD_PLATFORM", "COUNTERSPY_PLATFORM", "XTD_PLATFORM"]`

- `--private` _(optional)_  
  Restrict visibility and access to this app. Implies both `--no-upload` and `--no-delete`.

- `--no-upload` _(optional)_  
  Prevent other users from uploading new versions of this app.

- `--no-delete` _(optional)_  
  Prevent other users from deleting builds of this app.

#### ✅ Examples

Add a public Android app:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json add-application \
  --os android \
  --name "My App" \
  --package-id com.example.myapp
```

Add a private iOS app to a group:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json add-application \
  --os ios \
  --name "iOS Secure App" \
  --package-id com.example.iosapp \
  --group enterprise-apps \
  --private
```

---

### `update-application`

Updates the properties of an existing application registered in Verimatrix App Shield. You can change the app's name and its access permissions.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json update-application --application-id 12345 --name "New App Name"
```

#### 🔧 Options

- `--application-id` **(required)**  
  ID of the application to be updated. This value cannot be changed.

- `--name` **(required)**  
  New friendly name for the application.

- `--private` _(optional)_  
  Restrict the application from being visible to other users. Implies `--no-upload` and `--no-delete`.

- `--no-upload` _(optional)_  
  Prevent other users from uploading new builds for this app.

- `--no-delete` _(optional)_  
  Prevent other users from deleting builds for this app.

#### ✅ Examples

Update app name:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json update-application \
  --application-id 12345 \
  --name "My Renamed App"
```

Update app name and make it private:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json update-application \
  --application-id 12345 \
  --name "Secure App" \
  --private
```

---

### `delete-application`

Deletes an application from Verimatrix App Shield, including **all associated builds**. This operation is irreversible.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-application --application-id 12345
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application you want to delete.

#### ⚠️ Warning

This operation will permanently delete:

- The application record
- All uploaded builds for the application

Make sure you have backups or exports of important data before running this command.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-application --application-id 12345
```

---

### `set-signing-certificate`

Sets the signing certificate for a specific Android application. The certificate must be in PEM format.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-signing-certificate --application-id 12345 --file cert.pem
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

- `--file` **(required)**  
  Path to the PEM-encoded Android certificate file.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-signing-certificate \
  --application-id 12345 \
  --file ~/certs/my-cert.pem
```

---

### `delete-signing-certificate`

Deletes the signing certificate for a specific Android application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-signing-certificate --application-id 12345
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-signing-certificate \
  --application-id 12345
```

---

### `set-secondary-signing-certificate`

Sets the secondary signing certificate for a specific Android application. The certificate must be in PEM format.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-secondary-signing-certificate --application-id 12345 --file secondary-cert.pem
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

- `--file` **(required)**  
  Path to the PEM-encoded Android (secondary) certificate file.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-secondary-signing-certificate \
  --application-id 12345 \
  --file ~/certs/my-secondary-cert.pem
```

---

### `delete-secondary-signing-certificate`

Deletes the secondary signing certificate for a specific Android application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-secondary-signing-certificate --application-id 12345
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-secondary-signing-certificate \
  --application-id 12345
```

---

### `set-mapping-file`

Associates an R8/ProGuard mapping file with a specific Android build. This improves symbol readability and debugging of protected builds.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-mapping-file --build-id 98765 --file proguard.map
```

#### 🔧 Options

- `--build-id` **(required)**  
  ID of the Android build to associate the mapping file with.

- `--file` **(required)**  
  Path to the R8/ProGuard mapping file.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-mapping-file \
  --build-id 98765 \
  --file ~/builds/proguard.map
```

---

### `set-protection-configuration`

Sets the protection configuration for an application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-protection-configuration --application-id 12345 --file protConfig.json
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

- `--file` **(required)**  
  Path to the protection configuration JSON file.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-protection-configuration \
  --application-id 12345 \
  --file ~/protConfig.json
```

---

### `delete-protection-configuration`

Deletes the protection configuration for an application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-protection-configuration --application-id 12345
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-protection-configuration \
  --application-id 12345
```

---

### `set-certificate-pinning-configuration`

Sets the certificate pinning configuration for an application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-certificate-pinning-configuration --application-id 12345 --file certPinningConfig.json
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

- `--file` **(required)**  
  Path to the JSON file with the pinned certificate(s).

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-certificate-pinning-configuration \
  --application-id 12345 \
  --file ~/certPinningConfig.json
```

---

### `delete-certificate-pinning-configuration`

Deletes the certificate pinning configuration for an application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-certificate-pinning-configuration --application-id 12345
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to update.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-certificate-pinning-configuration \
  --application-id 12345
```

---

### `get-certificate-pinning-configuration`

Gets the certificate pinning configuration for an application.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-certificate-pinning-configuration --application-id 12345
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application to retrieve.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-certificate-pinning-configuration \
  --application-id 12345
```

---

### `set-build-certificate-pinning-configuration`

Sets the certificate pinning configuration for a build.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-build-certificate-pinning-configuration --build-id 12345 --file certPinningConfig.json
```

#### 🔧 Options

- `--build-id` **(required)**  
  The ID of the build to update.

- `--file` **(required)**  
  Path to the JSON file with the pinned certificate(s).

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-build-certificate-pinning-configuration \
  --build-id 12345 \
  --file ~/certPinningConfig.json
```

---

### `delete-build-certificate-pinning-configuration`

Deletes the certificate pinning configuration for a build.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-build-certificate-pinning-configuration --build-id 12345
```

#### 🔧 Options

- `--build-id` **(required)**  
  The ID of the build to update.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-build-certificate-pinning-configuration \
  --build-id 12345
```

---

### `get-certificate-pinning-configuration`

Gets the certificate pinning configuration for a build.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-build-certificate-pinning-configuration --build-id 12345
```

#### 🔧 Options

- `--build-id` **(required)**  
  The ID of the build to retrieve.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-build-certificate-pinning-configuration \
  --build-id 12345
```

---

### `list-builds`

Lists build artifacts associated with applications in Verimatrix App Shield. You can filter builds by application ID, build ID, or subscription type.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-builds
```

#### 🔧 Options

- `--application-id` _(optional)_  
  Returns builds associated with the given application.

- `--build-id` _(optional)_  
  Returns a single build identified by this build ID.

- `--subscription-type` _(optional)_  
  Specifies the subscription type.  
  Choices: `["APPSHIELD_PLATFORM", "COUNTERSPY_PLATFORM", "XTD_PLATFORM"]`

#### ✅ Examples

List all builds:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-builds
```

List builds for a specific application:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-builds --application-id 12345
```

Get a specific build by ID:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-builds --build-id 98765
```

Filter builds by subscription:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json list-builds --subscription-type XTD_PLATFORM
```

---

### `add-build`

Uploads a new mobile app build (Android `.apk` or iOS `.xcarchive`) to a registered application in Verimatrix App Shield.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json add-build --application-id 12345 --file path/to/app.apk
```

#### 🔧 Options

- `--application-id` **(required)**  
  The ID of the application the build belongs to.

- `--file` **(required)**
  Path to the build file. Supported formats:

  - Android: `.apk`
  - iOS: zipped `.xcarchive` folder

- `--subscription-type` _(optional)_  
  Specifies the subscription type.  
  Choices: `["APPSHIELD_PLATFORM", "COUNTERSPY_PLATFORM", "XTD_PLATFORM"]`

#### ✅ Examples

Upload an Android build:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json add-build \
  --application-id 12345 \
  --file ~/apps/my-app.apk
```

Upload an iOS build with subscription tier:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json add-build \
  --application-id 12345 \
  --file ~/apps/my-ios-app.xcarchive.zip \
  --subscription-type XTD_PLATFORM
```

---

### `delete-build`

Deletes a specific build from Verimatrix App Shield. This action is irreversible and will remove the associated protected binary.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-build --build-id 98765
```

#### 🔧 Options

- `--build-id` **(required)**  
  The ID of the build you want to delete.

#### ⚠️ Warning

This command will permanently delete the specified build, including any associated protection artifacts.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-build --build-id 98765
```

---

### `set-build-protection-configuration`

Sets the protection configuration for a build.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-build-protection-configuration --build-id 12345 --file protConfig.json
```

#### 🔧 Options

- `--build-id` **(required)**  
  The ID of the build to update.

- `--file` **(required)**  
  Path to the build protection configuration JSON file.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json set-build-protection-configuration \
  --build-id 12345 \
  --file ~/protConfig.json
```

---

### `delete-build-protection-configuration`

Deletes the protection configuration for a build.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-build-protection-configuration --build-id 12345
```

#### 🔧 Options

- `--build-id` **(required)**  
  The ID of the build to update.

#### ✅ Examples

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json delete-build-protection-configuration \
  --build-id 12345
```

---

### `protect-start`

Initiates the protection process for a build that was previously uploaded to Verimatrix App Shield. This starts the backend protection job.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-start --build-id 98765
```

#### 🔧 Options

- `--build-id` **(required)**  
  ID of the build to be protected.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-start --build-id 98765
```

Use `protect-get-status` to monitor the progress of this protection job after initiation.

---

### `protect-get-status`

Retrieves the current status of a protection job for a specific build. This includes progress updates, completion, or failure states.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-get-status --build-id 98765
```

#### 🔧 Options

- `--build-id` **(required)**  
  ID of the build whose protection status you want to check.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-get-status --build-id 98765
```

Use this command after starting a protection job with `protect-start` to monitor its progress.

---

### `protect-cancel`

Cancels an ongoing protection job for a specific build in Verimatrix App Shield. This can be used if the protection was started by mistake or is taking too long.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-cancel --build-id 98765
```

#### 🔧 Options

- `--build-id` **(required)**  
  ID of the build whose protection job should be cancelled.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-cancel --build-id 98765
```

Use this command if you need to abort a protection job started with `protect-start`.

---

### `protect-download`

Downloads a protected binary that was previously processed by Verimatrix App Shield.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-download --build-id 98765
```

#### 🔧 Options

- `--build-id` **(required)**  
  ID of the build whose protected output you want to download.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json protect-download --build-id 98765
```

Use this after confirming a successful protection job with `protect-get-status`.

---

### `get-account-info`

Retrieves information about the current user and their associated organization (customer) from Verimatrix App Shield.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-account-info
```

#### 🔧 Options

This command does not accept any additional arguments beyond the global `--api-key-file`.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-account-info
```

Returns details such as:

- Organization (customer) name and ID
- List of subscriptions
- User name and role

---

### `display-application-package-id`

Extracts and displays the application package ID from an input file (APK or XCARCHIVE).  
Useful when preparing to register an app using `add-application`.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json display-application-package-id --file path/to/app.apk
```

#### 🔧 Options

- `--file` **(required)**  
  Path to the input file:
  - Android: `.apk`
  - iOS: `.xcarchive` folder (typically zipped)

#### ✅ Examples

Display package ID from an APK:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json display-application-package-id --file my-app.apk
```

Display package ID from an iOS XCARCHIVE:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json display-application-package-id --file my-ios-app.xcarchive.zip
```

---

### `get-sail-config`

Retrieves the SAIL configuration for a specified platform and version.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-sail-config --os android
```

#### 🔧 Options

- `--os` **(required)**  
  Operating system to retrieve the SAIL config for.  
  Choices: `android`, `ios`

- `--version` _(optional)_  
  Specific SAIL version to retrieve configuration for. If omitted, retrieves the latest available version.

#### ✅ Examples

Get the latest SAIL config for Android:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-sail-config --os android
```

Get a specific version of SAIL config for iOS:

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-sail-config --os ios --version 1.2.3
```

---

### `get-version`

Retrieves the current version information for Verimatrix App Shield services and components. This includes platform-specific defender versions, SAIL versions, and templates.

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-version
```

#### 🔧 Options

This command does not take any additional options beyond the global `--api-key-file`.

#### ✅ Example

```bash
$ vmx-aps --api-key-file ~/Downloads/api-key.json get-version
```

**Example Output:**

```json
{
  "apkdefender": {
    "preanalysis-defaults": "20250401.json",
    "raven-apkdefender": "v4.8.3_20250401",
    "raven-template": "20250401.json",
    "sail": "1.46.4",
    "version": "4.8.3"
  },
  "apsdefenders": "2025.12.3-prod",
  "iosdefender": {
    "sail": "1.46.4",
    "version": "7.2.1"
  },
  "version": "2025.12.0-prod"
}
```

Use this command to verify deployed defender versions.
