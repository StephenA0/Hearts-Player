from operational import *
from make_decision import *

def get_hand(ref):
    hand = input("Input hand. Separate cards by spaces: ")
    while True:
        try:
            hand = sort_hand(hand.split(" "), ref)
            print("Initial Hand: " + str(hand))
            break
        except:
            hand = input("Invalid input. Try again: ")

    while True:
        is_pass = input("Passing round? Input Y or N: ")
        if is_pass == "Y":
            is_pass = True
            break
        elif is_pass == "N":
            is_pass = False
            break
        print("Invalid input. Try again. ")

    if is_pass:
        to_pass = pass_cards(hand, ref)
        print("Pass " + ", ".join(to_pass))
        while True:
            try:
                new_cards = input("Input received cards. Separate cards by spaces: ").split(" ")
                hand = sort_hand(hand[0] + hand[1] + hand[2] + hand[3] + new_cards, ref)
                break
            except:
                print("Invalid input. Try again. ")
    
    print("Game Hand: " + str(hand))
    return hand

def play_game(hand, ref):
    ranks = rel_ranks(hand, ref)
    remaining = [0, 0, 0, 0]
    for i in range(4):
        remaining[i] = 13 - len(hand[i])
    has_Qs = "Qs" in hand[1]

    has_players = [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]]
    ranks = rel_ranks(hand, ref)
    pts = [0, 0, 0, 0]
    trick_type = -1
    trick = [0, 0, 0, 0]
    hb = False
    ftrv = 100

    print("Who has the 2c? You are Player 0. Player 1 is left, Player 2 is across, and Player 3 is right. ")
    while True:
        try:
            leader = int(input("Input just the player number: "))
            break
        except:
            print("Invalid player number. Try again. ")

    for _ in range(13):
        if trick_type == 1:
            trick_type = 2
        best_rank = 100
        for i in range(4):
            curr_player = (leader + i) % 4
            if curr_player == 0:
                if i == 0:
                    trick[curr_player] = lead(hand, remaining, ranks, has_players, ref, has_Qs, trick_type, hb, ftrv)
                else:
                    trick[curr_player] = follow(hand, i, suit_value(trick[leader][1]), remaining, ranks, has_players, ref, best_rank, has_Qs, trick_type, ftrv)
                input("Play " + trick[curr_player] + ". Press ENTER once done. ")
            else:
                trick[curr_player] = input("Player " + str(curr_player) + " card: ")
                while not is_card(trick[curr_player], ref):
                    trick[curr_player] = input("Invalid card. Enter again: ")
            
            if trick[curr_player][1] == trick[leader][1]: #Correct suit
                best_rank = min(ref[trick[curr_player][0]], best_rank) #Update best_rank
            if trick[curr_player] == "Qs":
                trick_type = 1
                hb = True
            if trick[curr_player][1] == "h":
                hb = True
            if trick_type == -1 and curr_player != 0 and trick[curr_player][1] != "c": #first trick revealed void
                ftrv = curr_player
            
            update_info(hand, curr_player, remaining, ranks, has_players, trick[curr_player], trick[leader], ref)

        if trick_type != -1 and ftrv <= 3 and trick[ftrv][1] != trick[leader][1]: #ftrv player reveals void, no longer a threat
            ftrv = 100
        leader = winner(leader, trick, ref)
        pts[leader] += points(trick)
        if trick_type == -1:
            trick_type = 0

        print("Trick: " + str(trick))
        print("Hand: " + str(hand))
        print("Ranks: " + str(ranks))
        print("Remaining: " + str(remaining))
        print("Has players: " + str(has_players))
        print("New leader: " + str(leader))

    print("Round Points: " + str(pts))
    return pts

def was_shooter(shooter, total_pts):
    print("Player " + str(shooter) + " shot the moon!")
    if shooter == 0:
        shoot_update(total_pts, 0)
    else:
        print("Would player " + str(shooter) + " like to DROP 26 or ADD 26?")
        while True:
            drop_or_add = input("Input D or A: ")
            if drop_or_add == "D" or drop_or_add == "A":
                shoot_update(total_pts, shooter, drop_or_add)
                break
            else:
                print("Invalid input. Try again. ")
              
ref = rank_ref()
total_pts = [0, 0, 0, 0]
while max(total_pts) < 100 or total_pts.count(min(total_pts)) >= 2:
    hand = get_hand(ref)
    pts = play_game(hand, ref)
    if max(pts) == 26:
        was_shooter(pts.index(26), total_pts)
    else:
        for i in range(4):
            total_pts[i] += pts[i]

    print("Total Points: " + str(total_pts))

game_winner = total_pts.index(min(total_pts))
print("Player " + str(game_winner) + " wins!")

#Test Hand: 3h 9h Th As Js Ts 9s Kd Qd Jd 3d Tc Ac