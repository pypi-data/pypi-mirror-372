import re

# Feel free to add support for additional licenses, but ensure that each key
# follows the SPDX standard identifier for consistency. Each entry in this
# dictionary should use the SPDX license ID as the key, with the value being a
# tuple containing:
#   - A regex pattern to match the license text
#   - A sanitized version of the license name
# This setup maintains alignment with the SPDX standard while allowing flexible
# pattern matching.

# Common words to be removed from license names to standardize them for the
# matching search thus reducing regex cases
name_sanitization_terms = ["the", "software", "version", "license", "licence"]
sanitization_pattern = re.compile(rf"\b(?:{'|'.join(name_sanitization_terms)})\b", re.IGNORECASE)

COMMON_LICENSES = {
    "0BSD": (
        r"\b0bsd\b",
        "0BSD",
    ),
    "Apache-2.0": (
        r"\bapache[-\s]?v?2(\.0)?\b",
        "Apache 2.0",
    ),
    "Apache-1.0": (
        r"\bapache[-\s]?v?1(\.0)?\b",
        "Apache 1.0",
    ),
    "Apache-1.1": (
        r"\bapache[-\s]?v?1\.1\b",
        "Apache 1.1",
    ),
    "BSD-2-Clause": (
        r"\bbsd[-\s]?2[-\s]?clause\b",
        "BSD 2-Clause",
    ),
    "BSD-3-Clause": (
        r"\bbsd[-\s]?3[-\s]?clause\b",
        "BSD 3-Clause",
    ),
    "CC-BY-4.0": (
        r"\bcc[-\s]?by[-\s]?4\.0\b",
        "Creative Commons Attribution 4.0 International",
    ),
    "CC-BY-SA-4.0": (
        r"\bcc[-\s]?by[-\s]?sa[-\s]?4\.0\b",
        "Creative Commons Attribution ShareAlike 4.0 International",
    ),
    "CC-BY-ND-4.0": (
        r"\bcc[-\s]?by[-\s]?nd[-\s]?4\.0\b",
        "Creative Commons Attribution No Derivatives 4.0 International",
    ),
    "CC-BY-NC-4.0": (
        r"\bcc[-\s]?by[-\s]?nc[-\s]?4\.0\b",
        "Creative Commons Attribution NonCommercial 4.0 International",
    ),
    "CC-BY-NC-SA-4.0": (
        r"\bcc[-\s]?by[-\s]?nc[-\s]?sa[-\s]?4\.0\b",
        "Creative Commons Attribution NonCommercial ShareAlike 4.0 International",
    ),
    "CC-BY-NC-ND-4.0": (
        r"\bcc[-\s]?by[-\s]?nc[-\s]?nd[-\s]?4\.0\b",
        "Creative Commons Attribution NonCommercial No Derivatives 4.0 International",
    ),
    "CC-BY-3.0": (
        r"\bcc[-\s]?by[-\s]?3\.0\b",
        "Creative Commons Attribution 3.0 Unported",
    ),
    "CC-BY-SA-3.0": (
        r"\bcc[-\s]?by[-\s]?sa[-\s]?3\.0\b",
        "Creative Commons Attribution ShareAlike 3.0 Unported",
    ),
    "CC-BY-ND-3.0": (
        r"\bcc[-\s]?by[-\s]?nd[-\s]?3\.0\b",
        "Creative Commons Attribution No Derivatives 3.0 Unported",
    ),
    "CC-BY-NC-3.0": (
        r"\bcc[-\s]?by[-\s]?nc[-\s]?3\.0\b",
        "Creative Commons Attribution NonCommercial 3.0 Unported",
    ),
    "CC-BY-NC-SA-3.0": (
        r"\bcc[-\s]?by[-\s]?nc[-\s]?sa[-\s]?3\.0\b",
        "Creative Commons Attribution NonCommercial ShareAlike 3.0 Unported",
    ),
    "CC-BY-NC-ND-3.0": (
        r"\bcc[-\s]?by[-\s]?nc[-\s]?nd[-\s]?3\.0\b",
        "Creative Commons Attribution NonCommercial No Derivatives 3.0 Unported",
    ),
    "EPL-2.0": (
        r"\bepl[-\s]?2(\.0)?\b|\beclipse public v2\.0\b",
        "Eclipse Public 2.0",
    ),
    "EPL-1.0": (
        r"\bepl[-\s]?1(\.0)?\b|\beclipse public v1\.0\b",
        "Eclipse Public 1.0",
    ),
    "GPL-2.0-only": (
        r"\bgpl[-\s]?2(\.0)[-\s]?only\b",
        "GNU General Public v2.0 only",
    ),
    "GPL-2.0": (
        r"\bgpl[-\s]?2(\.0)\b",
        "GNU General Public v2.0",
    ),
    "GPL-2.0-or-later": (
        r"\bgpl[-\s]?2(\.0)?[-\s]?(?:or[-\s]?later|\+)?\b",
        "GNU General Public v2.0 or later",
    ),
    "GPL-3.0-only": (
        r"\bgpl[-\s]?3(\.0)?\b|\bgpl[-\s]?v3(\.0)?\b",
        "GNU General Public v3.0 only",
    ),
    "GPL-3.0-or-later": (
        r"\b(?:gnu\s+)?gpl(?:v)?3(\.0)?[-\s]?(?:or[-\s]?later|\+)?\b",
        "GNU General Public v3.0 or later",
    ),
    "LGPL-2.1-only": (
        r"\blgpl[-\s]?2\.1[-\s]?only\b",
        "GNU Lesser General Public v2.1 only",
    ),
    "LGPL-2.1-or-later": (
        r"\blgpl[-\s]?2\.1?[-\s]?(?:or[-\s]?later|\+)?\b",
        "GNU Lesser General Public v2.1 or later",
    ),
    "LGPL-3.0-only": (
        r"\blgpl[-\s]?3(\.0)?\b|\blgpl[-\s]?v3(\.0)?\b|\blgpl[-\s]?v3\b",
        "GNU Lesser General Public v3.0 only",
    ),
    "LGPL-3.0-or-later": (
        r"\blgpl[-\s]?3(\.0)?[-\s]?(?:or[-\s]?later|\+)?\b|"
        r"\blgpl[-\s]?v3(\.0)?[-\s]?(?:or[-\s]?later|\+)?\b"
        r"\blgpl[-\s]?v3\+\b",
        "GNU Lesser General Public v3.0 or later",
    ),
    "ISC": (
        r"\bisc\b",
        "ISC",
    ),
    "MIT": (
        r"\bmit\b",
        "MIT",
    ),
    "MPL-2.0": (
        r"\bmpl[-\s]?2(\.0)\b",
        "Mozilla Public 2.0",
    ),
    "OSL-3.0": (
        r"\bosl[-\s]?3(\.0)\b",
        "Open 3.0",
    ),
    "WTFPL": (
        r"\bwtfpl\b",
        "Do What The F*** You Want To Public (WTFPL)",
    ),
    "Zlib": (
        r"\bzlib\b",
        "Zlib",
    ),
    "Artistic-2.0": (
        r"\bartistic[-\s]?2(\.0)?\b",
        "Artistic 2.0",
    ),
    "BSL-1.0": (
        r"\bboost[-\s]?1(\.0)?\b",
        "Boost 1.0",
    ),
    "BlueOak-1.0.0": (
        r"\bBlueOak[-\s]?1\.0\.0\b",
        "Blue Oak Model 1.0.0",
    ),
    "PSF-2.0": (
        r"\bPSF[-\s]?2(\.0)?\b",
        "Python Foundation 2.0",
    ),
    "CC0-1.0": (
        r"\bCC0[-\s]?1\.0\b",
        "CC0-1.0",
    ),
    "Python-2.0": (
        r"\bpython[-\s]?2\.0\b",
        "Python 2.0",
    ),
}

INVERSE_LICENSES = {full_name: key for key, (_, full_name) in COMMON_LICENSES.items()}
