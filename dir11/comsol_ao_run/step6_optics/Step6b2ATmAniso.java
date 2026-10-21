import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;
import java.util.Locale;

public class Step6b2ATmAniso {
  static final String MPH="D:\\comsol_ao_run\\step6_optics\\step6_solved.mph";
  static final double P=2.8526131500e-6;
  static final int NB=114; static final double DX=P/NB;
  static final double NEFF=1.718501750, KAP=5.453034150e6, GAM=5.665351937e6;
  static final double M_TM=6.619814879e-08, CY=2.401805895e6, CZ=1.627650547e6, CMB=1.739958435e6;
  static final String PRO="-(5.404259965)";
  static final String PRE_E="-(4.886446036)";
  static final String HY="cos(5.453034150e6[1/m]*(y-hLn/2))^2";
  static final String HZ="sin(5.453034150e6[1/m]*(y-hLn/2))^2";
  public static void main(String[] a){
    try{
      ModelUtil.initStandalone(true);
      System.out.println("STEP6B2_START");
      System.out.println(String.format(Locale.US,"TMVAL neff=%.9f kappa=%.9e gamma=%.9e M=%.9e cY=%.9e cZ=%.9e cMB=%.9e",NEFF,KAP,GAM,M_TM,CY,CZ,CMB));
      Model m=ModelUtil.load("M6b2a",MPH);
      String[] dts=m.result().dataset().tags(); String ds=dts[dts.length-1];
      System.out.println("DATASET "+ds+" n="+dts.length);
      m.result().numerical().create("gf","EvalGlobal"); m.result().numerical("gf").set("data",ds);
      m.result().numerical("gf").set("expr",new String[]{"freq"}); m.result().numerical("gf").set("looplevelinput",new String[]{"all"});
      double[][] fr=m.result().numerical("gf").getReal(); int nf=fr[0].length;
      int ip=0,i320=0; double b1=9,b2=9;
      for(int i=0;i<nf;i++){ double f=fr[0][i]/1e9; if(Math.abs(f-3.3298)<b1){b1=Math.abs(f-3.3298);ip=i;} if(Math.abs(f-3.20)<b2){b2=Math.abs(f-3.20);i320=i;} }
      System.out.println(String.format(Locale.US,"FREQ_PICK ip=%d f_peak=%.9f i320=%d f320=%.9f nf=%d",ip,fr[0][ip]/1e9,i320,fr[0][i320]/1e9,nf));
      m.result().numerical().create("gc","EvalGlobal"); m.result().numerical("gc").set("data",ds);
      m.result().numerical("gc").set("expr",new String[]{"(1/p)*intLN(dnB*Eopt2)","(2/p)*intLN(dnB*Eopt2*exp(-i*2*pi*x/p))","(1/p)*intLN(eoB*Eopt2)","(2/p)*intLN(eoB*Eopt2*exp(-i*2*pi*x/p))","(1/p)*(intTop(v)-intBot(v))","(2/p)*(intTop(v*exp(-i*2*pi*x/p))-intBot(v*exp(-i*2*pi*x/p)))","intLN(abs(es.Ez))/intLN(1)","intLN(abs(es.Ez))/intLN(1)"});
      m.result().numerical("gc").set("looplevelinput",new String[]{"manual"}); m.result().numerical("gc").set("looplevel",new int[]{ip+1});
      double[][] cr=m.result().numerical("gc").getReal(); double[][] ci=m.result().numerical("gc").getImag();
      double[][] exp={{8.089971e-18,-3.734406e-17},{1.474535e-11,-3.156788e-11},{1.582663e-17,-9.202417e-17},{8.021639e-12,-2.803786e-11},{-1.021041e-17,4.713962e-17},{-3.583242e-11,1.363769e-10}};
      String[] nm={"PE_avg","PE_K","EO_avg","EO_K","MB_avg","MB_K"}; boolean ok=true;
      for(int i=0;i<6;i++){ double den=Math.hypot(exp[i][0],exp[i][1]); double rel=den>0?Math.hypot(cr[i][0]-exp[i][0],ci[i][0]-exp[i][1])/den:Math.hypot(cr[i][0],ci[i][0]); System.out.println(String.format(Locale.US,"LOADCHK %s new=(%.6e,%.6e) ref=(%.6e,%.6e) rel=%.3e",nm[i],cr[i][0],ci[i][0],exp[i][0],exp[i][1],rel)); if(rel>1e-6) ok=false; }
      System.out.println("LOADCHK_OK "+ok); if(!ok) throw new RuntimeException("load check failed");
      String[] items={"PEy","PE14y","EOy","PEz","MB"};
      String[] dn={PRO+"*((-0.026)*solid.eYY+0.090*solid.eXX+0.133*solid.eZZ)", PRO+"*((-0.075)*(-2*solid.eXZ))", PRO+"*(3.4e-12[m/V]*es.Ex)", PRE_E+"*(0.179*(solid.eYY+solid.eXX)+0.071*solid.eZZ)", ""};
      String[] wt={HY,HY,HY,HZ,""};
      double[] sc={CY,CY,CY,CZ,CMB};
      List<String> ex=new ArrayList<String>();
      ex.add("freq");
      for(int q=0;q<5;q++){
        if(q==4){
          ex.add("(1/p)*(intTop(v)-intBot(v))");
          ex.add("(2/p)*(intTop(v*exp(-i*2*pi*x/p))-intBot(v*exp(-i*2*pi*x/p)))");
        } else {
          ex.add("(1/p)*intLN("+dn[q]+"*"+wt[q]+")");
          ex.add("(2/p)*intLN("+dn[q]+"*"+wt[q]+"*exp(-i*2*pi*x/p))");
        }
      }
      for(int q=0;q<5;q++){
        for(int j=0;j<NB;j++){
          String ind="(x>="+j+"*p/114)*(x<"+(j+1)+"*p/114)";
          if(q==4) ex.add("(intTop(v*"+ind+")-intBot(v*"+ind+"))");
          else ex.add("intLN("+dn[q]+"*"+wt[q]+"*"+ind+")");
        }
      }
      System.out.println("EXPR_N "+ex.size());
      int[] picks={ip,i320};
      for(int pk=0;pk<2;pk++){
        String tag="gb"+pk;
        m.result().numerical().create(tag,"EvalGlobal");
        m.result().numerical(tag).set("data",ds);
        m.result().numerical(tag).set("expr",ex.toArray(new String[0]));
        m.result().numerical(tag).set("looplevelinput",new String[]{"manual"});
        m.result().numerical(tag).set("looplevel",new int[]{picks[pk]+1});
        double[][] r=m.result().numerical(tag).getReal();
        double[][] im=m.result().numerical(tag).getImag();
        double f=r[0][0]/1e9;
        int base=11;
        boolean ok2=true;
        for(int q=0;q<5;q++){
          double sa=0,sb=0,ka=0,kb=0;
          for(int j=0;j<NB;j++){
            double re=r[base+q*NB+j][0]*sc[q]/DX, ie=im[base+q*NB+j][0]*sc[q]/DX;
            double th=2*Math.PI*(j+0.5)*DX/P, c=Math.cos(th), s=-Math.sin(th);
            sa+=re*DX/P; sb+=ie*DX/P;
            ka+=(re*c-ie*s)*2*DX/P; kb+=(re*s+ie*c)*2*DX/P;
            System.out.println(String.format(Locale.US,"BINB2 f_GHz=%.9f item=%s j=%d xc_um=%.6f Re=%.6e Im=%.6e",f,items[q],j,(j+0.5)*DX*1e6,re,ie));
          }
          double ar=r[1+2*q][0]*sc[q], ai=im[1+2*q][0]*sc[q], kr=r[2+2*q][0]*sc[q], ki=im[2+2*q][0]*sc[q];
          double d1=Math.hypot(sa-ar,sb-ai)/Math.max(Math.hypot(ar,ai),1e-300);
          double d2=Math.hypot(ka-kr,kb-ki)/Math.max(Math.hypot(kr,ki),1e-300);
          System.out.println(String.format(Locale.US,"BINCHECK2 f=%.9f item=%s avg=(%.6e,%.6e) K=(%.6e,%.6e) avg_rel=%.3e K_rel=%.3e",f,items[q],ar,ai,kr,ki,d1,d2));
          if(d1>0.001||d2>0.005) ok2=false;
        }
        System.out.println("BINCHECK2_OK f="+f+" "+ok2);
      }
      ModelUtil.remove("M6b2a");
      System.out.println("STEP6B2_DONE");
    }catch(Throwable t){ System.out.println("STEP6B2_ABORT"); t.printStackTrace(System.out); }
  }
}
