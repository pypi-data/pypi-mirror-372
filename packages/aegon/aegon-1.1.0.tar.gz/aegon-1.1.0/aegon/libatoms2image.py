import os
import numpy as np
from ase.data import covalent_radii
from ase.data.colors import cpk_colors
#------------------------------------------------------------------------------------------
aspect_ratios_4by3 = {
    'a': (800, 600),     #SVGA
    'b': (1024, 768),    #XGA
    'c': (1280, 960),    #UXGA
    'd': (1600, 1200),
    'e': (2048, 1536),
    'f': (3200, 2400),
    'g': (6000, 4500),
}
aspect_ratios_16by9 = {
    'a': (1280, 720),    # HD
    'b': (1920, 1080),   # Full HD
    'c': (2560, 1440),   # QHD/2K
    'd': (3840, 2160),   # 4K UHD
    'e': (7680, 4320),   # 8K UHD
}
#------------------------------------------------------------------------------------------
bwd='0.12'                    # 0.15 GRUESO DE LOS ENLACES
dlv=0.15                      # GRUESO DEL LADO DEL CUBO
sphere_factor=float(0.55)     # 0.5 (g 1.5)
projection='orthographic'     # 'perspective'
reflection='reflection 0.0'
reflection_model='phong 1.0'  # 'specular'
radio_factor=float(1.30)      # 1.4 1.6 #ALCANCE DE LOS ENLACES
tmit = 0.35                   # transmit (transparencia) 0.35 0.75
#-----------------------------------------------------------------------------------------
def write_image(poscarin, basename, f=1.2, quality='f'):
    if quality in aspect_ratios_4by3:
        width, height = aspect_ratios_4by3[quality]
        print(f"Width: {width}, Height: {height}")
    else:
        print(f"'{quality}' is not defined.")
    poscarxx=poscarin.copy()
    matrix=poscarxx.cell
    a1=np.array(matrix[0,:])
    a2=np.array(matrix[1,:])
    a3=np.array(matrix[2,:])
    a=np.linalg.norm(a1)
    b=np.linalg.norm(a2)
    c=np.linalg.norm(a3)
    d=max([a,b,c])
    factor=f*d
    background1,background2,background3='2.0','2.0','2.0'
    light11,light12,light13='1','1','1'
    light21,light22,light23='1','1','1'
    camara_rotate='y*0.0'
    camara_loca1,camara_loca2,camara_loca3='0','0',str(factor)
    camara_look1,camara_look2,camara_look3='0','0','0'
    name_pov=basename+'.pov' 
    name_png=basename+'.png'
    opnew = open(name_pov,'w')
    print('global_settings { assumed_gamma 1.0 }', file=opnew)
    #print('# include \'colors.inc\'', file=opnew)
    print('background{color rgb<2.0, 2.0, 2.0>}\n', file=opnew)
    print('light_source {< 10, -8, -8> color rgb <1, 1, 1>}', file=opnew)
    print('light_source {< -8,  8,  8> color rgb <1, 1, 1>}\n', file=opnew)
    print('camera {%s location <0, 0, %4.2f> look_at <0, 0, 0> rotate y*0.0}\n' %(projection, factor), file=opnew)
    def primo(v1,v2):
        print('cylinder {<%9.6f, %9.6f, %9.6f> <%9.6f, %9.6f, %9.6f>, %6.4f pigment{color rgb <0, 0, 0>} finish {%s %s}}' %(-v1[0],v1[1],v1[2],-v2[0],v2[1],v2[2],dlv,reflection_model,reflection), file=opnew)
    #PARA QUE LA FIGURA SIEMPRE SALGA CENTRADA
    a0=-(a1+a2+a3)/2
    primo(a0,a0+a1)
    primo(a0,a0+a2)
    primo(a0,a0+a3)
    primo(a0+a1,a0+a1+a2)
    primo(a0+a1,a0+a1+a3)
    primo(a0+a2,a0+a1+a2)
    primo(a0+a2,a0+a2+a3)
    primo(a0+a3,a0+a1+a3)
    primo(a0+a3,a0+a2+a3)
    primo(a0+a1+a2,a0+a1+a2+a3)
    primo(a0+a1+a3,a0+a1+a2+a3)
    primo(a0+a2+a3,a0+a1+a2+a3)
    nn=len(poscarxx)
    for ii in range(nn):
        ni=poscarxx[ii].number
        ri=covalent_radii[ni]
        xxi,yyi,zzi=np.array(poscarxx[ii].position) + a0
        for jj in range(ii+1,nn):
            nj=poscarxx[jj].number
            rj= covalent_radii[nj]
            xxj,yyj,zzj=np.array(poscarxx[jj].position) + a0
            uij=poscarxx[jj].position - poscarxx[ii].position
            rr=np.linalg.norm(uij)
            uijn=uij/rr
            rt=rr/(ri+rj)
            if rt < radio_factor:
                xpm, ypm, zpm=(xxj+xxi)/2.0, (yyj+yyi)/2.0, (zzj+zzi)/2.0
                cpki=cpk_colors[ni]
                cpkj=cpk_colors[nj]
                kolori=f"<{', '.join(f'{x:.3f}' for x in cpki)}>"
                kolorj=f"<{', '.join(f'{x:.3f}' for x in cpkj)}>"
                otf=float(0.95)
                xxic=xxi+sphere_factor*otf*ri*uijn[0]
                yyic=yyi+sphere_factor*otf*ri*uijn[1]
                zzic=zzi+sphere_factor*otf*ri*uijn[2]
                xxjc=xxj-sphere_factor*otf*rj*uijn[0]
                yyjc=yyj-sphere_factor*otf*rj*uijn[1]
                zzjc=zzj-sphere_factor*otf*rj*uijn[2]
                print('cylinder {<%9.6f, %9.6f, %9.6f> <%9.6f, %9.6f, %9.6f> %s pigment {color rgb %s} finish {%s %s}}' %(-xxic,yyic,zzic,-xpm,ypm,zpm,bwd,kolori,reflection_model,reflection), file=opnew)
                print('cylinder {<%9.6f, %9.6f, %9.6f> <%9.6f, %9.6f, %9.6f> %s pigment {color rgb %s} finish {%s %s}}' %(-xpm,ypm,zpm,-xxjc,yyjc,zzjc,bwd,kolorj,reflection_model,reflection), file=opnew)
    for iatom in poscarxx:
        cr=covalent_radii[iatom.number]
        radii_div2=sphere_factor*cr
        cpk=cpk_colors[iatom.number]
        kolor=f"<{', '.join(f'{x:.3f}' for x in cpk)}>"
        xx, yy, zz=np.array(iatom.position) + a0
        s0='pigment {color rgb'
        print('sphere {<%9.6f, %9.6f, %9.6f>, %6.4f pigment {color rgb %s} finish {%s %s}}' %(-xx,yy,zz,radii_div2,kolor,reflection_model,reflection), file=opnew)
    opnew.close()
    comp='povray +A Display=Off Output_File_Type=N All_Console=Off Width='+str(width)+' Height='+str(height)+' '+name_pov+' > /dev/null 2>&1'
    os.system(comp)
    print('Output= %s %s' %(name_pov, name_png))
    doma='rm -f '+str(name_pov)
    os.system(doma)
#-----------------------------------------------------------------------------------------
