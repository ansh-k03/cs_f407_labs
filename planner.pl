connected(a, b).
connected(b, a).
connected(b, c).
connected(c, b).
can_move(From, To) :- connected(From, To).
valid_move(From, To) :- can_move(From, To).
valid_route([_]).
valid_route([From, To | Rest]) :- valid_move(From, To), valid_route([To | Rest]).
wet_road.
slippery :- wet_road.
reduce_speed :- slippery.
