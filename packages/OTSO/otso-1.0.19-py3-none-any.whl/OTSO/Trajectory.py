def trajectory(Stations,rigidity, customlocations=[], startaltitude=20,minaltitude=20,zenith=0,azimuth=0,maxdistance=100,maxtime=0,
           serverdata="OFF",livedata="OFF",vx=-500,vy=0,vz=0,by=5,bz=5,density=1,pdyn=0,Dst=0,
           G1=0,G2=0,G3=0,W1=0,W2=0,W3=0,W4=0,W5=0,W6=0,kp=0,Anum=1,anti="YES",year=2024,
           month=1,day=1,hour=12,minute=0,second=0,internalmag="IGRF",externalmag="TSY89",
           intmodel="Boris",coordsystem="GEO",gyropercent=15,magnetopause="Kobel",corenum=None, g=None, h=None,
           MHDfile=None,MHDcoordsys=None,spheresize=25, inputcoord="GDZ", Verbose=True):
    from .Parameters.functions import otso_trajectory
    import psutil

    if corenum is None:
       corenum = psutil.cpu_count(logical=False) - 2
       if corenum <= 0:
          corenum = 1
    
    arguments = locals()
    for arg in arguments:
       if arguments[arg] is None:
          arguments[arg] = []

    trajectory = otso_trajectory.OTSO_trajectory(Stations,rigidity, customlocations,startaltitude,
           minaltitude,zenith,azimuth,maxdistance,maxtime,serverdata,livedata,vx,vy,vz,by,bz,density,
           pdyn,Dst,G1,G2,G3,W1,W2,W3,W4,W5,W6,kp,Anum,anti,year,
           month,day,hour,minute,second,internalmag,externalmag,intmodel,
           coordsystem,gyropercent,magnetopause,corenum,g,h,MHDfile,MHDcoordsys,spheresize, inputcoord, Verbose)
    
    return trajectory