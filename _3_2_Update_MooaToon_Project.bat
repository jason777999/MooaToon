@echo off

echo ^============================================================
echo ==               Updating MooaToon Project                ==
echo ============================================================^


call _2_5_Settings.bat

cd %projectFolderName%

git checkout %projectBranchName%
git pull --depth=50 origin %projectBranchName%
git merge origin/%projectBranchName%

if not %errorlevel% == 0 (
    color 04
    echo Merge failed, please run Force Clean after backup files.
    pause
)else (
    echo %projectFolderName% successfully update.
    timeout /t 10
)