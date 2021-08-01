#Basic Methods ------------------------------------------------------------------------------------------------------------------------
def is_card(card, ref):
    return len(card) == 2 and card[0] in ref and card[1] in ["h", "s", "d", "c"]

def suit_value(suit_letter):
    if suit_letter == "h":
        return 0
    if suit_letter == "s":
        return 1
    if suit_letter == "d":
        return 2
    if suit_letter == "c":
        return 3
    else:
        suit_letter = input("Invalid suit letter. Input suit letter again: ")
        return suit_value(suit_letter)

def max_card(card_a, card_b, rank_ref):
    if card_a[1] != card_b[1]:
        return card_a
    else:
        if rank_ref[card_a[0]] < rank_ref[card_b[0]]:
            return card_a
        else:
            return card_b

def winner(leader, trick, rank_ref): 
    winner = leader
    for i in range(1, 4):
        if max_card(trick[winner], trick[(leader + i) % 4], rank_ref) != trick[winner]:
            winner = (leader + i) % 4
    
    return winner

def points(trick):
    points = 0
    for card in trick:
        if card[1] == "h":
            points += 1
        elif card == "Qs":
            points += 13
    
    return points

#Sorting Methods -----------------------------------------------------------------------------------------------------------------------
def insert_sorted(card, suit_list, ref):
    index = 0
    try:
        while ref[card[0]] > ref[suit_list[index][0]]:
            index += 1
    except IndexError:
        pass

    suit_list.insert(index, card)

def sort_hand(hand, ref):
    if len(hand) != 13:
        raise Exception("Invalid hand length. ")
    sorted_hand = [[], [], [], []]
    for card in hand:
        if not is_card(card, ref):
            raise Exception("Invalid card. ")
        suit = suit_value(card[1])
        insert_sorted(card, sorted_hand[suit], ref)
    
    return sorted_hand

#Rank Methods --------------------------------------------------------------------------------------------------------------------------
def rank_ref():
    dic = {}
    dic["A"] = 1
    dic["K"] = 2
    dic["Q"] = 3
    dic["J"] = 4
    dic["T"] = 5
    for i in range(2, 10):
        dic[str(i)] = 15 - i
    
    return dic

def rel_ranks(hand, ref):
    ranks = [[], [], [], []]
    for i in range(4):
        for card in hand[i]:
            ranks[i].append(ref[card[0]])

    return ranks

#Update Methods -------------------------------------------------------------------------------------------------------------------------
def update_info(hand, player, remaining, ranks, has_players, card, lead, ref):
    suit = suit_value(card[1])

    if player == 0:
        index = hand[suit].index(card)
        for i in range(index + 1, len(hand[suit])):
            ranks[suit][i] -= 1
        hand[suit].pop(index)
        ranks[suit].pop(index)
    else:
        remaining[suit] -= 1
        index = len(hand[suit]) - 1
        while index >= 0:
            if ref[card[0]] > ref[hand[suit][index][0]]:
                break
            ranks[suit][index] -= 1
            index -= 1
        lead_suit = suit_value(lead[1])
        if lead_suit != suit:
            if player in has_players[lead_suit]:
                has_players[lead_suit].remove(player)

def shoot_update(total_pts, shooter, choice = "A"):
    if choice == "D" or max(total_pts) >= 74 and min(total_pts) + 26 < total_pts[shooter]:
        total_pts[shooter] -= 26
    else:
        for i in range(4):
            if i != shooter:
                total_pts[i] += 26