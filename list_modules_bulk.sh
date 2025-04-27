total_repos=$(find -H $HOME/verilog_testing/verilog-repos/saverepo/ -mindepth 3 -maxdepth 3 -type d | wc -l)
current_repo=0

find -H $HOME/verilog_testing/verilog-repos/saverepo/ -mindepth 3 -maxdepth 3 -type d | while IFS= read -r repo; do
    current_repo=$((current_repo + 1))
    percent=$((100 * current_repo / total_repos))
    echo -ne "($current_repo/$total_repos, $percent%) Processing repo: $repo............................................\r"
    bash list_modules.sh "$repo"
done
echo -e "\nDone!"