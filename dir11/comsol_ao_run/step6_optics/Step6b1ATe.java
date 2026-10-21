import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

public class Step6b1ATe {
  static final String MPH="D:\\comsol_ao_run\\step6_optics\\step6_solved.mph";
  static final double P=2.8526131500e-6, H=500e-9, NO=2.211, NEFF=1.963773541, KAP=4.1182443e6, GAM=6.85106642e6;
  static final int NB=114; static final double DX=P/NB;
  static final String PRE="-("+String.format(Locale.US,"%.9f",Math.pow(NO,3)/2)+")";
  static final String E2="cos(4.1182443e6[1/m]*(y-hLn/2))^2";
  public static void main(String[] a){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6B1_START");
      double et=Math.cos(KAP*H/2), core=H/2+Math.sin(KAP*H)/(2*KAP), clad=et*et/GAM, N=core+clad;
      System.out.println(String.format(Locale.US,"NVAL N=%.12e core=%.12e clad=%.12e E_top=%.12e neff=%.9f kappa=%.9e gamma=%.9e",N,core,clad,et,NEFF,KAP,GAM));
      double cA=NO/(NEFF*N), cMB=(NO*NO-1)*et*et/(2*NEFF*N);
      System.out.println(String.format(Locale.US,"SCALE cA=%.9e cMB=%.9e",cA,cMB));
      Model m=ModelUtil.load("M6b1",MPH);
      String[] dts=m.result().dataset().tags(); String ds=dts[dts.length-1];
      System.out.println("DATASET "+ds+" n="+dts.length);
      m.component("comp1").variable().create("vA");
      m.component("comp1").variable("vA").selection().geom("geom1",2);
      m.component("comp1").variable("vA").selection().named("selLN");
      String pre="-("+String.format(Locale.US,"%.9f",Math.pow(NO,3)/2)+")";
      m.component("comp1").variable("vA").set("E2A","cos("+String.format(Locale.US,"%.9e",KAP)+"[1/m]*(y-hLn/2))^2");
      m.component("comp1").variable("vA").set("S4A","(-2*solid.eXZ)");
      m.component("comp1").variable("vA").set("dnPE_A_TE",pre+"*("+String.format(Locale.US,"%.6f",0.090)+"*solid.eYY+("+String.format(Locale.US,"%.6f",-0.026)+")*solid.eXX+"+String.format(Locale.US,"%.6f",0.133)+"*solid.eZZ)");
      m.component("comp1").variable("vA").set("dnPE14_A_TE",pre+"*(("+String.format(Locale.US,"%.6f",0.075)+")*S4A)");
      m.component("comp1").variable("vA").set("eo22_A_TE",pre+"*("+String.format(Locale.US,"%.6e",3.4e-12)+"[m/V]*(-es.Ex))");
      m.component("comp1").variable("vA").set("eo13_A_TE",pre+"*("+String.format(Locale.US,"%.6e",8.6e-12)+"[m/V]*es.Ez)");
      // frequency list
      m.result().numerical().create("gf","EvalGlobal"); m.result().numerical("gf").set("data",ds);
      m.result().numerical("gf").set("expr",new String[]{"freq"}); m.result().numerical("gf").set("looplevelinput",new String[]{"all"});
      double[][] fr=m.result().numerical("gf").getReal(); int nf=fr[0].length;
      int ip=0,i320=0; double b1=9,b2=9;
      for(int i=0;i<nf;i++){ double f=fr[0][i]/1e9; if(Math.abs(f-3.3298)<b1){b1=Math.abs(f-3.3298);ip=i;} if(Math.abs(f-3.20)<b2){b2=Math.abs(f-3.20);i320=i;} }
      System.out.println(String.format(Locale.US,"FREQ_PICK ip=%d f_peak=%.9f i320=%d f320=%.9f nf=%d",ip,fr[0][ip]/1e9,i320,fr[0][i320]/1e9,nf));
      m.result().numerical().create("gv","EvalGlobal"); m.result().numerical("gv").set("data",ds);
      m.result().numerical("gv").set("expr",new String[]{"intLN("+E2+")/intLN(1)","intLN("+PRE+"*(0.090*solid.eYY+(-0.026)*solid.eXX+0.133*solid.eZZ))/intLN(1)"});
      m.result().numerical("gv").set("looplevelinput",new String[]{"manual"}); m.result().numerical("gv").set("looplevel",new int[]{ip+1});
      double[][] vr=m.result().numerical("gv").getReal(); System.out.println(String.format(Locale.US,"VARCHK E2A_avg=%.6e dnPE_avg=%.6e",vr[0][0],vr[1][0]));
      // load check at peak: B avg/K raw
      m.result().numerical().create("gc","EvalGlobal"); m.result().numerical("gc").set("data",ds);
      m.result().numerical("gc").set("expr",new String[]{"(1/p)*intLN(dnB*Eopt2)","(2/p)*intLN(dnB*Eopt2*exp(-i*2*pi*x/p))","(1/p)*intLN(eoB*Eopt2)","(2/p)*intLN(eoB*Eopt2*exp(-i*2*pi*x/p))","(1/p)*(intTop(v)-intBot(v))","(2/p)*(intTop(v*exp(-i*2*pi*x/p))-intBot(v*exp(-i*2*pi*x/p)))","intLN(abs(es.Ez))/intLN(1)","intLN(abs(es.Ez))/intLN(1)"});
      m.result().numerical("gc").set("looplevelinput",new String[]{"manual"}); m.result().numerical("gc").set("looplevel",new int[]{ip+1});
      double[][] cr=m.result().numerical("gc").getReal(); double[][] ci=m.result().numerical("gc").getImag();
      double[][] exp={{8.089971e-18,-3.734406e-17},{1.474535e-11,-3.156788e-11},{1.582663e-17,-9.202417e-17},{8.021639e-12,-2.803786e-11},{-1.021041e-17,4.713962e-17},{-3.583242e-11,1.363769e-10}};
      String[] nm={"PE_avg","PE_K","EO_avg","EO_K","MB_avg","MB_K"}; boolean ok=true;
      for(int i=0;i<6;i++){ double den=Math.hypot(exp[i][0],exp[i][1]); double rel=den>0?Math.hypot(cr[i][0]-exp[i][0],ci[i][0]-exp[i][1])/den:Math.hypot(cr[i][0],ci[i][0]); System.out.println(String.format(Locale.US,"LOADCHK %s new=(%.6e,%.6e) ref=(%.6e,%.6e) rel=%.3e",nm[i],cr[i][0],ci[i][0],exp[i][0],exp[i][1],rel)); if(rel>1e-6) ok=false; }
      System.out.println("LOADCHK_OK "+ok); if(!ok) throw new RuntimeException("load check failed");
      System.out.println(String.format(Locale.US,"EZAVG absEz_avg=%.6e",cr[6][0]));
      // bins feature exprs
      List<String> ex=new ArrayList<String>();
      ex.add("freq");
      String[][] refs={{PRE+"*(0.090*solid.eYY+(-0.026)*solid.eXX+0.133*solid.eZZ)",E2},{PRE+"*((0.075)*(-2*solid.eXZ))",E2},{PRE+"*(3.4e-12[m/V]*(-es.Ex))",E2},{PRE+"*(8.6e-12[m/V]*es.Ez)",E2},{"MBX",""}};
      for(int q=0;q<5;q++){ String dn=refs[q][0]; if(dn.equals("MBX")){ ex.add("(1/p)*(intTop(v)-intBot(v))"); ex.add("(2/p)*(intTop(v*exp(-i*2*pi*x/p))-intBot(v*exp(-i*2*pi*x/p)))"); } else { String e2=refs[q][1]; ex.add("(1/p)*intLN("+dn+"*"+e2+")"); ex.add("(2/p)*intLN("+dn+"*"+e2+"*exp(-i*2*pi*x/p))"); } }
      for(int q=0;q<5;q++){ String dn=refs[q][0]; for(int j=0;j<NB;j++){ String ind="(x>="+j+"*p/114)*(x<"+(j+1)+"*p/114)"; if(dn.equals("MBX")) ex.add("(intTop(v*"+ind+")-intBot(v*"+ind+"))"); else ex.add("intLN("+dn+"*"+refs[q][1]+"*"+ind+")"); } }
      System.out.println("EXPR_N "+ex.size());
      int[] picks={ip,i320};
      for(int pick=0;pick<2;pick++){
        int idx=picks[pick]; String tag="gb"+pick;
        m.result().numerical().create(tag,"EvalGlobal"); m.result().numerical(tag).set("data",ds);
        m.result().numerical(tag).set("expr",ex.toArray(new String[0])); m.result().numerical(tag).set("looplevelinput",new String[]{"manual"});
        m.result().numerical(tag).set("looplevel",new int[]{idx+1});
        double[][] r=m.result().numerical(tag).getReal(); double[][] im=m.result().numerical(tag).getImag();
        double f=r[0][0]/1e9;
        int base=11;
        double[][][] dn=new double[5][NB][2];
        for(int q=0;q<5;q++) for(int j=0;j<NB;j++){ dn[q][j][0]=r[base+q*NB+j][0]; dn[q][j][1]=im[base+q*NB+j][0]; }
        double[] sc={cA,cA,cA,cA,cMB};
        double[] sumA=new double[5],sumI=new double[5],sumKA=new double[5],sumKI=new double[5];
        for(int q=0;q<5;q++) for(int j=0;j<NB;j++){ double xc=(j+0.5)*DX; double th=2*Math.PI*xc/P; double c=Math.cos(th),s=-Math.sin(th); double re=dn[q][j][0]*sc[q]/DX, ie=dn[q][j][1]*sc[q]/DX; sumA[q]+=re*DX/P; sumI[q]+=ie*DX/P; sumKA[q]+=(re*c-ie*s)*DX*2/P; sumKI[q]+=(re*s+ie*c)*DX*2/P; }
        boolean ok2=true;
        for(int q=0;q<5;q++){ double aref=r[1+q*2][0]*sc[q], iref=im[1+q*2][0]*sc[q], kref=r[2+q*2][0]*sc[q], kiref=im[2+q*2][0]*sc[q]; double d1=Math.hypot(sumA[q]-aref,sumI[q]-iref)/Math.max(Math.hypot(aref,iref),1e-300); double d2=Math.hypot(sumKA[q]-kref,sumKI[q]-kiref)/Math.max(Math.hypot(kref,kiref),1e-300); System.out.println(String.format(Locale.US,"BINCHECK f=%.9f q=%d avg_rel=%.3e K_rel=%.3e",f,q,d1,d2)); if(d1>0.001||d2>0.005) ok2=false; }
        System.out.println("BINCHECK_OK "+ok2); if(!ok2) throw new RuntimeException("bin self-check failed");
        for(int q=0;q<5;q++) for(int j=0;j<NB;j++) System.out.println(String.format(Locale.US,"BINB1 f_GHz=%.9f q=%d j=%d xc_um=%.6f Re=%.6e Im=%.6e",f,q,j,(j+0.5)*DX*1e6,dn[q][j][0]*sc[q]/DX,dn[q][j][1]*sc[q]/DX));
        // windows
        double[] tot=new double[NB]; double[] totI=new double[NB];
        for(int j=0;j<NB;j++){ tot[j]=dn[0][j][0]+dn[1][j][0]+dn[2][j][0]+dn[3][j][0]+dn[4][j][0]; totI[j]=dn[0][j][1]+dn[1][j][1]+dn[2][j][1]+dn[3][j][1]+dn[4][j][1]; }
        for(int wi=0;wi<3;wi++){ int mw=(int)Math.round((wi==0?0.3e-6:(wi==1?0.5e-6:0.8e-6))/DX); double bA=-1; int bj=0; for(int j0=0;j0<NB;j0++){ double sr=0,si=0; for(int q2=0;q2<mw;q2++){ int jj=(j0+q2)%NB; sr+=tot[jj]; si+=totI[jj]; } sr/=mw; si/=mw; if(Math.hypot(sr,si)>bA){bA=Math.hypot(sr,si);bj=j0;} }
          double[] mv=new double[5]; double[] mi=new double[5]; for(int q=0;q<5;q++){ double sr=0,si=0; for(int q2=0;q2<mw;q2++){ int jj=(bj+q2)%NB; sr+=dn[q][jj][0]*sc[q]/DX; si+=dn[q][jj][1]*sc[q]/DX; } mv[q]=sr/mw; mi[q]=si/mw; }
          System.out.println(String.format(Locale.US,"WINB1 f_GHz=%.9f w_um=%.2f j0=%d x0_um=%.6f PE_Re=%.6e PE_Im=%.6e PE14_Re=%.6e PE14_Im=%.6e EO22_Re=%.6e EO22_Im=%.6e EO13_Re=%.6e EO13_Im=%.6e MB_Re=%.6e MB_Im=%.6e",f,(wi==0?0.3:(wi==1?0.5:0.8)),bj,bj*DX*1e6,mv[0],mi[0],mv[1],mi[1],mv[2],mi[2],mv[3],mi[3],mv[4],mi[4]));
        }
        // harmonics
        for(int q=0;q<4;q++){ for(int nh=1;nh<=7;nh++){ double sr=0,si=0; for(int j=0;j<NB;j++){ double xc=(j+0.5)*DX; double th=2*Math.PI*nh*xc/P; double re=(q==0?(dn[0][j][0]+dn[1][j][0]):q==1?(dn[2][j][0]+dn[3][j][0]):q==2?dn[4][j][0]:tot[j]); double ie=(q==0?(dn[0][j][1]+dn[1][j][1]):q==1?(dn[2][j][1]+dn[3][j][1]):q==2?dn[4][j][1]:totI[j]); sr+=(re*Math.cos(th)-ie*(-Math.sin(th))); si+=(re*(-Math.sin(th))+ie*Math.cos(th)); }
            System.out.println(String.format(Locale.US,"HARMB1 f_GHz=%.9f q=%d nh=%d amp=%.6e",f,q,nh,Math.hypot(sr,si)*2/NB)); } }
      }
      ModelUtil.remove("M6b1");
      System.out.println("STEP6B1_DONE");
    }catch(Throwable t){ System.out.println("STEP6B1_ABORT"); t.printStackTrace(System.out); }
  }
}
