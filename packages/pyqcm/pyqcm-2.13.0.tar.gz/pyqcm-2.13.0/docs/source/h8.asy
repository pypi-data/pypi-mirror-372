texpreamble("\input preamble.tex");
real L=30;
real d = 7.5*72;
int n = 45;

pair e1 = (L,0);
pair e2 = rotate(120)*e1;
pair b1 = e1-e2;
pair b2 = 2*e1+e2;
pair E2 = 2*e1-2*e2;
pair E1 = 4*e1+2*e2;

path p1 = e1 -- (e1+e2);
path p2 = e1 -- (2*e1);
path p3 = e1 -- (-e2);

pen IC_pen = linetype("4 4")+deepgreen;
pen C_pen = deepgreen+linewidth(1);

path[] u = -e1--(0,0)--(e1+e2)^^(0,0)--(-e2);
path[] U = shift(-e1)*u^^shift(e1)*rotate(180)*u;
path b = (3*e1)--(2*e2+e1)--(-3*e1)--(-2*e2-e1)--cycle;

int r = 6;
for(int i=-r+1; i<r; ++i){
	for(int j=-r+1; j<r; ++j){
		draw(shift(i*b1+j*b2)*p1,IC_pen);
		draw(shift(i*b1+j*b2)*p2,IC_pen);
		draw(shift(i*b1+j*b2)*p3,IC_pen);
	}
}

filldraw(b,lightblue+opacity(0.4),blue);

dotfactor=8;

r = 3;
for(int i=-r+1; i<r; ++i){
	for(int j=-r+1; j<r; ++j){
		draw(shift(i*E1+j*E2)*U,C_pen);
		dot(shift(i*E1+j*E2)*U,deepblue);
//		draw(shift(i*E1+j*E2)*b,blue+linetype("6 6"));
	}
}

draw("$\mathbf{E}_1$",(0,0)--E1,2N,EndArrow(8));
draw("$\mathbf{E}_2$",(0,0)--E2,2S,EndArrow(8));

dotfactor=12;

dot(U, deepred);

draw("$\mathbf{e}_1$",shift(3*e2)*((0,0)--e1),EndArrow(8));
draw("$\mathbf{e}_2$",shift(3*e2)*((0,0)--e2),EndArrow(8));

real a1 = 5*L;
real a2 = 4*L;
clip((a1,a2)--(-a1,a2)--(-a1,-a2)--(a1,-a2) -- cycle);
