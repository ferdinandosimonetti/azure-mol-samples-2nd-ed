@echo off
az account get-access-token| jq  -r .accessToken