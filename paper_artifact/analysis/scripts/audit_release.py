#!/usr/bin/env python3
"""Strict local release scan; does not print potentially sensitive match values.

Patterns in this scanner and its documentation are expected references, not
credentials. Reports identify file, line and rule only. No network or models.
"""
import re
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RULES={
 'absolute_home_path':r'/home/[^\s]+|/Users/[^\s]+|[A-Za-z]:\\(?:Users|Documents)\\',
 'local_username':r'syedalihaider|linux_guest|guest-MS-7E27',
 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'github_token':r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b',
 'aws_key':r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'credential_assignment':r'''(?i)(?:password|api[_-]?key|access[_-]?token|secret[_-]?key)\s*[=:]\s*["'][A-Za-z0-9_+/=-]{12,}["']''',
 'signed_url':r'(?i)(?:X-Amz-(?:Signature|Credential)|[?&](?:token|signature|sig|auth)=)[^\s"<>]+',
 'private_ipv4':r'\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
 'ipv4_address':r'(?<![\w.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?![\w.])',
 'bearer_credential':r'(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._=-]{12,}',
 'ipv6_address':r'(?i)(?<![\w:])(?:[0-9a-f]{1,4}:){3,}[0-9a-f:]{1,4}(?![\w:])',
 'loopback_or_internal':r'(?i)\b(?:localhost|127\.0\.0\.1|[a-z0-9-]+\.(?:local|internal))\b',
 'ssh_or_cookie':r'(?i)(?:/\.ssh/|id_rsa|id_ed25519|cookie\s*:\s*[^\s])',
 'email_address':r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
}


def main():
    findings=[];scanned=0;pdf_count=0
    selected=[]
    for directory,dirs,names in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in ('.venv','venv','.git'))
        selected.extend(Path(directory)/name for name in names)
    for p in sorted(selected):
        if not p.is_file():continue
        rel=p.relative_to(ROOT).as_posix()
        if '__pycache__' in p.parts:findings.append((rel,0,'cache'));continue
        if p.suffix=='.pdf':
            pdf_count+=1
            # Own generated PDF objects are scanned for raw credential/path strings.
            text=p.read_bytes().decode('latin-1')
        else:
            try:text=p.read_text()
            except UnicodeDecodeError:findings.append((rel,0,'unreviewed_binary'));continue
        scanned+=1
        # Literal rules in the scanner and audit documentation are intentional.
        if rel in ['analysis/scripts/audit_release.py','RELEASE_SAFETY_AUDIT.md']:continue
        for n,line in enumerate(text.splitlines(),1):
            for rule,pattern in RULES.items():
                if re.search(pattern,line):findings.append((rel,n,rule))
        if p.name in ['.env','credentials','cookies.sqlite'] or p.suffix in ['.pem','.key']:
            findings.append((rel,0,'credential_filename'))
    for path,line,rule in findings:print(f'REVIEW {path}:{line} ({rule}); value withheld')
    print(f'Scanned {scanned} files including {pdf_count} generated PDFs; {len(findings)} review findings. Scanner/audit pattern literals are documented exceptions.')
    return 1 if findings else 0


if __name__=='__main__':sys.exit(main())
