# puyo-music
Soumission pour le Ludum Elried

C'est un jeu (non fini) dans le genre de puyo mais dans lequel il faut regrouper des accords pour faire disparaitre les pièces, représentants des notes.
Une fois détruit, l'accord apparait sur la timeline en bas et est lu en boucle par le backend. (timeline unique pour les deux joueurs)

Pour l'instant l'algo n'accepte que des accords parfaits (tierce mineure ou majeure, quinte juste), et travaille uniquement sur la gamme de Do.

Le backend est au choix : 
- le buzzer du PC (paquet beep, il faut faire le chmod sur l'exe, winsound de python sous windows)
- la commande play sous linux qui produit des sons sinusoidaux
- linuxsampler via midi (rtmidi). Config uniquement pour JACK pour l'instant

Si vous voulez les samples que j'utilise avec linux sampler c'est par ici : https://www.linuxsampler.org/instruments.html (Maestro Concert Grand v2, j'ai pas testé le reste)

Pour l'instant la mort n'existe pas, remplire jusqu'à la case de départ ne reset que le tableau.

Les dégats augmentent avec le combo mais c'est pas très équilibré (un 3hit explose automatiquement l'adversaire :> vu que la formule c'est 20 ^ combo :>). Le renvoie de dégat existe cependant. (tant qu'on a pas reçu les dégats on peut les annuler voir les renvoyer)

Touches =
UP = Hard Drop
DOWN = Descente rapide
LEFT = Gauche
Right = Droite

Idem pour le p2 sur le numpad avec les touches 8 5 4 6

Le code est bardé de bugs
Le code est aussi bien rangé commenté et conçu que mon cerveau :>
Ne lisez pas le code pour votre santé.

Pas de menus.

Voilà :)
Moi je vais me coucher :> (7h35)

PS: je suis pas sûr de l'intérêt du concept ni de ses possibles améliorations... m'enfin le tout est d'avoir fait qqch :>

