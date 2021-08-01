import math
from operational import *

#Passing Methods ------------------------------------------------------------------------------------------
def pass_cards(hand, ref):
    def initial_pass(space):
        if "2c" in hand[3]:
            to_pass.append(hand[3].pop())
            space -= 1

        if has_Qs:
            if len(hand[1]) <= 2:
                if hand[1][0] == "As" or hand[1][0] == "Ks":
                    to_pass.extend(hand[1]) #pass both high spades (As/Qs or Ks/Qs)
                    hand[1] = []
                    space -= 2
                else:
                    to_pass.append(hand[1].pop(0)) #pass the Qs
                    space -= 1
        else:
            if len(hand[1]) == 4 and hand[1][0] == "As" and hand[1][1] == "Ks":
                to_pass.append(hand[1].pop(0))
                to_pass.append(hand[1].pop(0))
                space -= 2
            elif len(hand[1]) <= 3:
                while hand[1] and (hand[1][0] == "As" or hand[1][0] == "Ks"): #Passes As and Ks if included
                    to_pass.append(hand[1].pop(0))
                    space -= 1

        return space

    def get_top(space):
        top = 0
        if top < len(hand[0]) and hand[0][top] == "Ah":
            top += 1
        if top < len(hand[0]) and hand[0][top] == "Kh":
            top += 1

        if not hand[2] and not hand[3]:
            while space and len(hand[0]) > top:
                to_pass.append(hand[0].pop(top))
                space -= 1
            while space and hand[1]: #If reached, len(hand[1]) is very high (9+)
                to_pass.append(hand[1].pop(0))
                space -= 1
    
        return (top, space)
    
    def mid_pass_has_Qs(space):
        if (hand[3] and len(hand[3]) <= space) or (hand[2] and len(hand[2]) <= space):
            if hand[3] and len(hand[3]) <= space:
                voidable = 3
            if hand[2] and len(hand[2]) <= space: #prioritize voiding diamonds if possible
                voidable = 2
        
            to_pass.extend(hand[voidable])
            space -= len(hand[voidable])
            hand[voidable] = []
        else:
            if not hand[2]:
                shortest = 3
            elif not hand[3]:
                shortest = 2
            else:
                if len(hand[3]) < len(hand[2]): #work to empty diamonds in tiebreak
                    shortest = 3
                else:
                    shortest = 2
        
            while space:
                to_pass.append(hand[shortest].pop(0))
                space -= 1
        
        return space
    
    #Goal: Between clubs/diamonds, make voids, but also 
    #rid yourself of the more dangerous suit (highest kth_lowest)
    def mid_pass_no_Qs(space):
        kth_lowest_club = 14 - ref[hand[3][-1][0]] if hand[3] else 0
        kth_lowest_diam = 14 - ref[hand[2][-1][0]] if hand[2] else 0

        if kth_lowest_club > kth_lowest_diam: #Diamonds passed in tiebreak (clubs safer via first trick)
            while space and hand[3]:
                to_pass.append(hand[3].pop(0))
                space -= 1
        else:
            while space and hand[2]:
                to_pass.append(hand[2].pop(0))
                space -= 1
        
        return space

    def pass_remaining(space):
        while space and len(hand[0]) > top and ref[hand[0][top][0]] <= 6: #anything 9h - Qh
            to_pass.append(hand[0].pop(top))
            space -= 1

        while space and hand[2]: #empty diamonds
            to_pass.append(hand[2].pop(0))
            space -= 1
    
        while space and hand[3]: #empty clubs
            to_pass.append(hand[3].pop(0))
            space -= 1
    
        #At this point, pass high spades. This case is rare.

        while space and hand[1]:
            to_pass.append(hand[1].pop(0))
            space -= 1
    
        while space and len(hand[0]) > top:
            to_pass.append(hand[0].pop(top))
            space -= 1
        
        return space

    to_pass = []
    space = 3
    has_Qs = "Qs" in hand[1]

    space = initial_pass(space)
    top, space = get_top(space)
    if has_Qs:
        space = mid_pass_has_Qs(space)
    else:
        space = mid_pass_no_Qs(space)

    #At this point, you have done your best to void a club/diamond suit (for no_Qs, a dangerous one)

    space = pass_remaining(space)
    return to_pass

#Auxiliary Decision-Making Methods -----------------------------------------------------------------------
def play_under(hand, suit, best_rank, rank_ref, pos):
    if pos == 3 and rank_ref[hand[suit][-1][0]] < best_rank:
        return hand[suit][0]
    for i in range(len(hand[suit])):
        if rank_ref[hand[suit][i][0]] > best_rank:
           return hand[suit][i]

    return hand[suit][-1]

def frem_val(suit, has_players):
    num_voids = 3 - len(has_players[suit])

    if num_voids == 0:
        return 2.25 + 1.5*(suit == 0) #3.75 for hearts
    elif num_voids == 1:
        return 1.75 + 1.25*(suit == 0) #3 for hearts
    elif num_voids == 2:
        return 1.25 + 0.75*(suit == 0) #2 for hearts
    else:
        return 0

def qs_risk(remaining, suit, pos):
    s = sum(remaining)
    r = remaining[suit] 
    t = math.ceil(s/3)

    if r == 0: #None remaining, play low
        return 1

    #Probs are probabilities of post voids
    p_one_void = 0
    p_two_voids = 0
    if pos == 0: 
        p_one_void = (2**r - 2) / 3**(r-1)
        p_two_voids = 1 / 3**(r-1)
    elif pos == 1:
        p_one_void = 2*(2**r - 1) / 3**r
        p_two_voids = 1 / 3**r
    elif pos == 2:
        p_one_void = 2**r / 3**r
    
    #Note r == s is not possible, since suit != 1 and Qs is in remaining
    #Thus, there is no division by 0 risk
    risk = (p_one_void + 2*p_two_voids) * t/(s-r)
    return risk

def aggro(hand, remaining, threshold):
    void_cards = 0
    for i in range(4):
        if not hand[i]:
            void_cards += remaining[i]
    #prob that a void suit is never led (crude but decent)
    prob = 0
    if sum(remaining) != 0:
        prob = (1 - void_cards/(4/3*sum(remaining))) ** sum(remaining)/3
    
    if prob > threshold: #Risk too high, construct voids
        return 0
    else: #Fall back on created voids
        return -1

#Determines whether, in a "duel", you would be able
#to repeatedly play under your opponent. Win_duel
#suits are very safe and useful in late-game play.
def win_duel(ranks, remaining):
    opp_ranks = []
    for i in range(1, remaining + len(ranks) + 1):
        if i not in ranks:
            opp_ranks.append(i)
            
    for i in range(1, min(len(ranks), len(opp_ranks)) + 1):
        if ranks[-i] < opp_ranks[-i]:
            return False
    return True

#Leading Methods --------------------------------------------------------------------------------------
def lead(hand, remaining, ranks, has_players, rank_ref, has_Qs, trick_type, hb, ftrv):
    if trick_type == -1: #First trick
        return "2c"
    elif trick_type == 0: #Early trick
        if has_Qs:
            return early_lead_has_Qs(hand, remaining, ranks, has_players, rank_ref, hb)
        else:
            return early_lead_no_Qs(hand, remaining, ranks, has_players, rank_ref, hb, ftrv)
    else: #trick_type == 1 (Qs trick) not possible, so trick_type == 2 (Late trick)
        return late_lead(hand, remaining, ranks, has_players, rank_ref, hb)

#Goal: Make a strategic void, then dip
#Best void: Has most future remaining cards after you empty yours in a suit

#We compute a probability assessing the chances our void suit is led
#If the probability is too low, we construct more voids (lead high)
#If it is high enough, we fall back on our created voids (lead low)

def early_lead_has_Qs(hand, remaining, ranks, has_players, rank_ref, hb):

    index = aggro(hand, remaining, 0.15) #Tells whether to construct or fall back

    if remaining[1] == 1 and 1 not in ranks[1]: #1 remaining As/Ks spade
        return "Qs"
    elif remaining[1] == 2 and 1 not in ranks[1] and 2 not in ranks[1]: #As, Ks only spades out there
        return "Qs"
    
    diamond_frem = remaining[2] - frem_val(2, has_players)*len(hand[2]) if remaining[2] else -1000
    club_frem = remaining[3] - frem_val(3, has_players)*len(hand[3]) if remaining[3] else -1000

    if hb and hand[0]:
        heart_frem = remaining[0] - frem_val(0, has_players)*len(hand[0]) if remaining[0] and ranks[0] != list(range(1, len(hand[0]) + 1)) else -1000
        if (not hand[2] or heart_frem > diamond_frem) and (not hand[3] or heart_frem > club_frem) and heart_frem > -1000:
            return hand[0][-1] #Lead low to avoid winning the heart trick

    if not hand[2] and not hand[3]: #Only spades and unusable/unproductive hearts. Deflect at all costs (lowest spade)
        if hand[1][-1] == "Qs":
            return hand[1][0] #potentially deflects if Ks/Qs. If As/Ks/Qs, there's nothing you can do, you're screwed.
        return hand[1][-1]

    if not hand[2]:
        if club_frem == -1000:
            return play_under(hand, 1, 3, rank_ref, 0) #If it so happens this is not doable, 
            #you have only Qs+ spades and unusable suits. You're screwed anyway.
        return hand[3][index] #play high/low depending on void_prob

    if not hand[3]:
        if diamond_frem == -1000:
            return play_under(hand, 1, 3, rank_ref, 0)
        return hand[2][index] #play high/low depending on void_prob

    #Lead suit (diamonds/clubs) with most future remaining cards
    if diamond_frem == club_frem == -1000:
        return play_under(hand, 1, 3, rank_ref, 0)
    elif diamond_frem > club_frem:
        return hand[2][index]
    else:
        return hand[3][index]

#A very qs_risky suit you will certainly lose is actually great.
    #You must have the lowest card and in some cases the 2nd lowest.
        #Lowest is ALWAYS safe though. But 2nd lowest is often safe.
    #The 3rd lowest is too risky to assume to be a loser.

def early_lead_no_Qs(hand, remaining, ranks, has_players, rank_ref, hb, ftrv):
    def lead_risky(risk, suit):
        if not hand[suit] or not remaining[suit]:
            return False
        kth_lowest = len(hand[suit]) + remaining[suit] + 1 - ranks[suit][-1]
        if risk > 0.5 and kth_lowest == 1: #you can confidently screw someone with a >50% chance. Killshot.
            return True
        if len(has_players[suit]) == 3 and kth_lowest == 2:
            if remaining[suit] >= 4 and risk > 0.4: #Works if 4+ remaining cards are not consolidated in one player.
                return True
        return False
            
    if hand[1] and rank_ref[hand[1][0][0]] >= 4: #has spade, but no As, Ks, or Qs
        return hand[1][0]

    diamond_risk = qs_risk(remaining, 2, 0)
    if lead_risky(diamond_risk, 2):
        return hand[2][-1]

    club_risk = 1/3 if ftrv != 100 else qs_risk(remaining, 3, 0)

    if lead_risky(club_risk, 3):
        return hand[3][-1]

    if hb and hand[0]:
        heart_risk = qs_risk(remaining, 0, 0)
        if (not hand[2] or heart_risk < diamond_risk) and (not hand[3] or heart_risk < club_risk):
            return hand[0][-1]
        
    if not hand[2]:
        try:
            if club_risk < 0.25:
                return hand[3][0]
            return hand[3][-1]
        except IndexError:
            try:
                return hand[1][-1]
            except IndexError:
                return hand[0][-1]
    if not hand[3]:
        try:
            if diamond_risk < 0.25:
                return hand[2][0]
            return hand[2][-1]
        except IndexError:
            try:
                return hand[1][-1]
            except IndexError:
                return hand[0][-1]
    
    if diamond_risk <= club_risk: #Leads diamonds in tiebreakers
        if diamond_risk < 0.25:
            return hand[2][0]
        return hand[2][-1]
    else:
        if club_risk < 0.25:
            return hand[3][0]
        return hand[3][-1]

#Slide out on shortest win_duel suit
    #Aim to throw riskier suits out once making voids
#If no win_duel suit, then...(algorithm implemented below)

def late_lead(hand, remaining, ranks, has_players, rank_ref, hb):
    win_duel_suits = []

    for i in range(4):
        if i == 0 and not hb:
            continue
        elif hand[i] and remaining[i] > 0:
            if win_duel(ranks[i], remaining[i]):
                win_duel_suits.append(i)
        
    if not win_duel_suits: 
        #Every suit is potentially risky. We have a few options.
        #We could lead low in hearts if it's losable to drain the heart pool.
        #We could lead high and slip out
            #I.e. we have the lowest card in a suit and still some remaining after we do this
        #We need a default option
            #On slippable suits, slip out on the shortest one
                #Aim for voids

        lowest_ranks = []
        for suit in range(4):
            if not hand[suit]: 
                lowest_ranks.append(9999)
            elif not hb and suit == 0:
                lowest_ranks.append(999)
            elif not remaining[suit]:
                lowest_ranks.append(100)
            elif ranks[suit] == list(range(1, len(ranks[suit]) + 1)):
                lowest_ranks.append(50)
            else:
                lowest_ranks.append(len(hand[suit]) + remaining[suit] - ranks[suit][-1] + 1)

        min_rank = min(lowest_ranks)

        if min_rank == 1: #aim for void in tiebreak
            index = lowest_ranks.index(1)
            for i in range(4):
                if lowest_ranks[i] == 1:
                    if len(hand[i]) < len(hand[index]):
                        index = i
        elif min_rank == 2: #aim for two has_players and highest remaining in tiebreak
            index = lowest_ranks.index(2)
            has_two = len(has_players[index]) >= 2
            for i in range(4):
                if lowest_ranks[i] == 2 and len(has_players[i]) >= 2:
                    if not has_two:
                        index = i
                        has_two = True
                    elif remaining[i] >= remaining[index]:
                        index = i
        elif min_rank == 3: #aim for three has_players and highest remaining in tiebreak
            index = lowest_ranks.index(3)
            has_three = len(has_players[index]) == 3
            for i in range(4):
                if lowest_ranks[i] == 3 and len(has_players[i]) == 3:
                    if not has_three:
                        index = i
                        has_three = True
                    elif remaining[i] >= remaining[index]:
                        index = i
        else: #You're pretty screwed on this trick. Aim to make a void. Avoid hearts.
            index = lowest_ranks.index(min_rank)
            if index == 0:
                second_min = min(lowest_ranks[1:])
                if second_min < 50:
                    index = lowest_ranks.index(second_min)
            for i in range(1, 4):
                if lowest_ranks[i] <= 50: #Anything which is playable/has some remaining left
                    if len(hand[i]) <= len(hand[index]):
                        index = i
        
        return hand[index][-1]

    #Lead low in the shortest win_duel suit (aim to make a void)
    shortest = win_duel_suits[0]
    for suit in win_duel_suits:
        if len(hand[suit]) < len(hand[shortest]): #Earlier suits win tiebreaks
            shortest = suit
    return hand[shortest][-1]

#Following Methods -------------------------------------------------------------------------------------
def follow(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank, has_Qs, trick_type, ftrv):
    if trick_type == -1: #First trick
        return first_trick_follow(hand, has_Qs, rank_ref)
    if trick_type == 0: #Early trick
        return early_follow(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank, has_Qs, ftrv)
    elif trick_type == 1: #Qs trick
        return qs_trick(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank)
    else: #Late trick
        return late_follow(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank)

def first_trick_follow(hand, has_Qs, ref):
    if hand[3]:
        return hand[3][0]
    elif not has_Qs and hand[1] and (hand[1][0] == "As" or hand[1][0] == "Ks"):
        return hand[1][0]
    elif hand[2]:
        return hand[2][0]
    elif hand[1]:
        if hand[1][0] == "Qs" and len(hand[1]) >= 2:
            return hand[1][1]
        return hand[1][0] #returns Qs in extreme Qs + all hearts case
    else: 
        return hand[0][0] #Extremely rare case (dealt all hearts), but accounted for
    
def early_follow(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank, has_Qs, ftrv):
    if suit == 0 and hand[0]:
       return play_under(hand, 0, best_rank, rank_ref, pos)
    elif suit == 1 and hand[1]:
        if has_Qs:
            if best_rank <= 2: #As or Ks has been played
                return "Qs"
            elif hand[1][0] == "Qs" and len(hand[1]) >= 2:
                return hand[1][1]
            else:
                return hand[1][0]
        elif pos == 3 or (pos == 2 and 1 not in has_players[1]) or (pos == 1 and has_players[1] == [3]):
            return hand[1][0]
        elif best_rank == 1:
            return hand[1][0] #throws Ks under As
        else:
            if "As" in hand[1] and "Ks" in hand[1]:
                if len(hand[1]) >= 3:
                    return hand[1][2]
                return hand[1][0] #You only have As/Ks
            elif "As" in hand[1] or "Ks" in hand[1]: #This is an XOR via the first if statement
                if len(hand[1]) >= 2:
                    return hand[1][1]
                return hand[1][0] #Only one spade, either As or Ks
            else:
                return hand[1][0] #No As/Ks (or Qs), so throw top spade
    elif has_Qs:
        return early_follow_has_Qs(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank)
    else:
        return early_follow_no_Qs(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank, ftrv)

#Note: suit is not spades
def early_follow_has_Qs(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank):
    if hand[suit]: 
        index = aggro(hand, remaining, 0.15) #Measures our level of future safety
        has_ahead = 0
        for i in range(pos + 1, 4):
            if i - pos in has_players[suit]:
                has_ahead += 1

        if remaining[suit] <= has_ahead or index == -1:
            return play_under(hand, suit, best_rank, rank_ref, pos)
        return hand[suit][0]

    return "Qs"

#Note: if spades, player has spade void
def early_follow_no_Qs(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank, ftrv):
    if hand[suit]:
        if qs_risk(remaining, suit, pos) > 0.25 or (suit == 3 and ftrv <= 3 - pos):
            return play_under(hand, suit, best_rank, rank_ref, pos)
        return hand[suit][0]
    
    if hand[1] and (hand[1][0] == "As" or hand[1][0] == "Ks"):
        return hand[1][0]

    if bool(hand[0]) + bool(hand[2]) + bool(hand[3]) == 1:
        if hand[0]:
            return hand[0][0]
        if hand[2]:
            return hand[2][0]
        if hand[3]:
            return hand[3][0]
    
    heart_rem = remaining[0] if hand[0] else 999
    diamond_rem = remaining[2] if hand[2] else 999
    club_rem = remaining[3] if hand[3] else 999

    #Note suits with remaining == 0 are win_duel (which is what we want)
    if hand[0] and win_duel(ranks[0], remaining[0]):
        heart_rem = 100
    if hand[2] and win_duel(ranks[2], remaining[2]):
        diamond_rem = 100
    if hand[3] and win_duel(ranks[3], remaining[3]):
        club_rem = 100

    if len(hand[0]) == 1 and len(has_players[0]) >= 2 and ranks[0][0] == remaining[0] and remaining[0] >= 5: #likely safe 2nd lowest
        heart_rem = 50
    if len(hand[2]) == 1 and len(has_players[2]) >= 2 and ranks[2][0] == remaining[2] and remaining[2] >= 5: #likely safe 2nd lowest
        diamond_rem = 50
    if len(hand[3]) == 1 and len(has_players[3]) >= 2 and ranks[3][0] == remaining[3] and remaining[3] >= 5: #likely safe 2nd lowest
        club_rem = 50

    if hand[1] and min(heart_rem, diamond_rem, club_rem) >= 50:
        return hand[1][0]

    risky_suit = 0
    if diamond_rem < min(heart_rem, club_rem):
        risky_suit = 2
    elif club_rem < min(heart_rem, diamond_rem):
        risky_suit = 3
    
    return hand[risky_suit][0]

def qs_trick(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank):
    if hand[suit]: #play under, aim to lose.
        return play_under(hand, suit, best_rank, rank_ref, pos)
    return late_follow(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank)

#Late game basic strategy: take high, lead low. For hearts, generally avoid taking the trick.
def late_follow(hand, pos, suit, remaining, ranks, has_players, rank_ref, best_rank):
    if hand[suit]:
        index = aggro(hand, remaining, 0.25) #Measures our level of future safety
        has_ahead = 0
        for i in range(pos + 1, 4):
            if i - pos in has_players[suit]:
                has_ahead += 1
        
        if remaining[suit] <= has_ahead or (index == -1 and suit != 0):
            return play_under(hand, suit, best_rank, rank_ref, pos)
        
        if suit == 0:
            under_card = play_under(hand, suit, best_rank, rank_ref, pos)
            if rank_ref[under_card[0]] > best_rank: #We can successfully play under
                return under_card
            if pos == 3: #You have to take, so play high (accounted for in play_under)
                return under_card

            kth_lowest = len(hand[suit]) + remaining[suit] + 1 - ranks[suit][-1] #must be >= 2
            if pos == 2:
                if 1 not in has_players[0] or kth_lowest >= 3: #You must take, or it is likely you will anyway
                    return hand[0][0]
                return hand[0][-1] #kth_lowest == 2, 1 likely has a heart
            if pos == 1: #Last remaining case. If statement included for readability
                if (1 not in has_players[0] and 2 not in has_players[0]) or kth_lowest >= 3:
                    return hand[0][0]
                return hand[0][-1] #kth_lowest == 2, 1 or 2 likely has a heart

        return hand[suit][0] #Take high
    
    losing_suits = [] #non-win_duel suits (potentially unsafe)
    for i in range(4):
        if hand[i] and remaining[i] > 0:
            if not win_duel(ranks[i], remaining[i]):
                losing_suits.append(i)
    
    if not losing_suits: #Every suit is win_duel -- you're very safe
        if hand[1]:
            return hand[1][0]
        elif hand[2]:
            return hand[2][0]
        elif hand[3]:
            return hand[3][0]
        else:
            return hand[0][0] #Last priority, since they will always be thrown under anyway in heart tricks

    shortest_loser = losing_suits[0]
    for s in losing_suits:
        if len(hand[s]) < len(hand[shortest_loser]): #Hearts win tiebreaks
            shortest_loser = s
    return hand[shortest_loser][0]