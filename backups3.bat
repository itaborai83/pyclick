cmd /c aws s3 sync DADOS\STAGING s3://itaborai83-pyclick-bkp-staging
cmd /c aws s3 sync DADOS\IMPORT s3://itaborai83-pyclick-bkp-import --exclude *.db