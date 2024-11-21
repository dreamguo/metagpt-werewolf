group_id=1
# echo "Running 11 player game for group $group_id"
python start_game.py --n_player 6 --n_games 1 --group $group_id 2>&1 | tee "logs/output_1_11_Group${group_id}.txt"

# group_id=7
# python start_game.py --n_player 10 --n_games 1 --group $group_id 2>&1 | tee "logs/output_1_11_Group_final.txt"
