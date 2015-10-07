# stableMarriage
Gale Shapley python script for student arrangement into sections

The gist of the algorithm is that every student has a complete list of their preferences and every client has a complete list of their preferences (which for non-commercial clients we randomize).

We randomly take a student who is not assigned to a client, and go through his preferences in order. The first client from the preferences that still has spots left will take him.

If a student wants to get onto a team that is full, they can ask to get in. The client will look at its list of preferences, and if the student that wants to get is higher in the client's preferences than the client's current lowest ranked student, the client will kick out the lowest ranked student and accept the slightly higher ranked one.

The student who is kicked out is returned back into the list and we keep this going until the algo stabilizes with a solution