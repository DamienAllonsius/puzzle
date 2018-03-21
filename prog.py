import numpy as np

def convertir(n,pos):
	assert(pos>=-1 and pos<=n),"position impossible !"
	if pos==-1:
		return n-1
	elif pos==n:
		return 1
	else:
		return pos

#~ Sens conventionnel (trigo) Est, North, West, South
def voisins(n,pos_piece):
	V=[[pos_piece[0],convertir(n,pos_piece[1]+1)], [convertir(n,pos_piece[0]-1),pos_piece[1]],[pos_piece[0],convertir(n,pos_piece[1]-1)],[convertir(n,pos_piece[0]+1),pos_piece[1]]];
	return V
print(voisins(5,[0,0]))
#~ type_piece, par exemple : (1,-1,1,1).
#~ type_voisin : liste de 4 type_piece (toujours en (E,N,W,S))
#~ Voisin non defini => (0,0,0,0)

def rotation(l):
	k=range(0,4)
	for p in range(0,4):
		k[p]=l[((p+1)%4)]
	return k

def determine_piece(type_piece):
	s=sum(type_piece)
	m=0
	if not(s==0):
		return s
	else:
		for k in range(2,4):
			m=m + sum(type_piece[k-2:k])
		if m==0:
			return 0
		else:
			return -1

def compatible(type_voisins,type_piece):
	global a
	b=False
	corres=[2,3,0,1]
	count=1
	r=list(type_piece)
	det_piece = determine_piece(type_piece)
	while not(b) and (count<5):
		b=True
		for k in range(0,4):
			b= b and ((r[k]*(type_voisins[k][corres[k]])==0) or (r[k]*(type_voisins[k][corres[k]])==-1)) #~ emboitement possible
			b= b and not(det_piece==determine_piece(type_voisins[k]))	#~ pas deux pieces adjacentes identiques
		count=count+1
		r=rotation(r)
	return b

type_voisins=[[-1,-1,-1,-1],[-1,1,1,-1],[-1,-1,1,-1],[-1,-1,-1,-1]]
type_piece=[1,1,1,1]
#~ print(type_voisins)
print(compatible(type_voisins,type_piece))
#~ print(type_voisins[1][1])

#~ Coeur du programme 

def matrice_pavage(i,j):
	M=[]
	v=[]
	z=[0,0,0,0]
	for k in range(0,j):
		v.append(z)
	for k in range(0,i):
		M.append(v)
	return M
	
N=input("nombre de lignes et de colonnes ? ")
M=matrice_pavage(N,N)
#~ liste_pieces=input("rentrer les pieces possibles : ") 
liste_pieces=[[1,1,1,1],[-1,-1,-1,-1]]  
#~ sous la forme [[1,1,1,1],[-1,1,-1,1]]

def number2coordinate(n):
	global N 
	return [(n-n%N)/N,n%N]
	

def pavage_periodique(n,pieces_possibles_2):
	global M
	global N
	global liste_pieces
	print(M)
	pos_piece=number2coordinate(n)
	pieces_possibles=list(pieces_possibles_2)
	#~ global j
	#~ Si la somme de liste_pieces n'est pas nulle, renvoyer 0
#~ 
	#~ Sinon : 
	#~ print(M)
	if n==(N*N):
		return True
	else:
		if pieces_possibles==[]:
			M[pos_piece[0]][pos_piece[1]]=[0,0,0,0]
			return False
		else:
			#~ Pour avoir les voisins
			v=voisins(N,pos_piece)
			les_voisins=[]
			for k in range(0,4):
				les_voisins.append(M[v[k][0]][v[k][1]])
				
			if compatible(les_voisins,pieces_possibles[0]):
				M[pos_piece[0]][pos_piece[1]]=pieces_possibles[0]

				if pavage_periodique(n+1,liste_pieces):
					return True
				else:
					M[pos_piece[0]][pos_piece[1]]=[0,0,0,0]
					del pieces_possibles[0]
					pavage_periodique(n,pieces_possibles)
			else:
				M[pos_piece[0]][pos_piece[1]]=[0,0,0,0]
				del pieces_possibles[0]
				pavage_periodique(n,pieces_possibles)

pavage_periodique(0,liste_pieces)
print(M)

