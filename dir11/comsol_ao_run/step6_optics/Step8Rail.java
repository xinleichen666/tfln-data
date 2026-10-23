import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

/** Step 8: per-length C of the feed rails on the anchored (unreleased) chip, 2D electrostatics.
 *  Stack (assumed, parametric): LN slab HLN on SiO2 BOX HBOX on Si HSI (high-resistivity Si treated as a lossless dielectric).
 *  Rails: signal strip WS, gap G, ground strip WG, thickness TM, on top of the LN. Signal at 1 V, ground 0 V.
 *  Each geometry is solved twice: with the real permittivities (C) and with all eps = 1 (C0, gives L = 1/(c^2 C0)).
 *  Prints RAIL8 lines; R per length is computed in post-processing from the strip cross sections. */
public class Step8Rail {
  static final double HLN=400e-9, HBOX=2e-6, HSI=500e-6, HAIR=500e-6, TM=100e-9;
  static final double E_LN_X=28.0, E_LN_Y=44.0, E_OX=3.9, E_SI=11.7;

  public static void main(String[] args){
    try{
      ModelUtil.initStandalone(true);
      double[][] cases={{5,5,50},{10,5,50},{20,5,50},{10,10,50},{20,10,50},{50,10,100},{80,20,80}};
      for(double[] c:cases) for(boolean vac:new boolean[]{false,true}) run(c[0]*1e-6,c[1]*1e-6,c[2]*1e-6,vac);
    }catch(Throwable t){ System.out.println("STEP8_ABORT"); t.printStackTrace(System.out); }
  }

  static void run(double ws,double g,double wg,boolean vac)throws Exception{
    Model m=ModelUtil.create("M8");
    m.component().create("c",true);
    GeomSequence geo=m.component("c").geom().create("g",2);
    geo.lengthUnit("m");
    double W=1.2e-3, x0=-W/2;
    rect(geo,"si",x0,-HBOX-HSI,W,HSI);
    rect(geo,"ox",x0,-HBOX,W,HBOX);
    rect(geo,"ln",x0,0,W,HLN);
    rect(geo,"air",x0,HLN,W,HAIR);
    double xs=-ws/2, xg=ws/2+g;
    rect(geo,"rs",xs,HLN,ws,TM);
    rect(geo,"rg",xg,HLN,wg,TM);
    geo.run();
    double t=1e-9;
    box(m,"dSi",2,x0-t,-x0+t,-HBOX-HSI-t,-HBOX+t);
    box(m,"dOx",2,x0-t,-x0+t,-HBOX-t,t);
    box(m,"dLn",2,x0-t,-x0+t,-t,HLN+t);
    box(m,"dAirB",2,x0-t,-x0+t,HLN-t,HLN+HAIR+t);
    box(m,"dS",2,xs-t,xs+ws+t,HLN-t,HLN+TM+t);
    box(m,"dG",2,xg-t,xg+wg+t,HLN-t,HLN+TM+t);
    m.component("c").selection().create("dMet","Union");
    m.component("c").selection("dMet").set("input",new String[]{"dS","dG"});
    m.component("c").selection().create("dAir","Difference");
    m.component("c").selection("dAir").set("add",new String[]{"dAirB"});
    m.component("c").selection("dAir").set("subtract",new String[]{"dMet"});
    m.component("c").selection().create("dAll","Explicit");
    m.component("c").selection("dAll").all();
    m.component("c").selection().create("dDiel","Difference");
    m.component("c").selection("dDiel").set("add",new String[]{"dAll"});
    m.component("c").selection("dDiel").set("subtract",new String[]{"dMet"});
    m.component("c").selection().create("bS","Adjacent"); m.component("c").selection("bS").set("input",new String[]{"dS"});
    m.component("c").selection().create("bG","Adjacent"); m.component("c").selection("bG").set("input",new String[]{"dG"});

    m.component("c").physics().create("es","Electrostatics","g");
    m.component("c").physics("es").selection().named("dDiel");
    String[][] eps={{"dSi",f(E_SI),f(E_SI)},{"dOx",f(E_OX),f(E_OX)},{"dLn",f(E_LN_X),f(E_LN_Y)},{"dAir","1","1"}};
    int k=0;
    for(String[] e:eps){
      String tg="cc"+(k++);
      m.component("c").physics("es").create(tg,"ChargeConservation",2);
      m.component("c").physics("es").feature(tg).selection().named(e[0]);
      m.component("c").physics("es").feature(tg).set("epsilonr_mat","userdef");
      String ex=vac?"1":e[1], ey=vac?"1":e[2];
      m.component("c").physics("es").feature(tg).set("epsilonr",new String[]{ex,"0","0","0",ey,"0","0","0",ey});
    }
    m.component("c").physics("es").create("term1","Terminal",1);
    m.component("c").physics("es").feature("term1").selection().named("bS");
    m.component("c").physics("es").feature("term1").set("TerminalType","Voltage");
    m.component("c").physics("es").feature("term1").set("V0","1[V]");
    m.component("c").physics("es").create("gnd1","Ground",1);
    m.component("c").physics("es").feature("gnd1").selection().named("bG");

    m.component("c").mesh().create("mesh","g");
    m.component("c").mesh("mesh").create("ft","FreeTri");
    m.component("c").mesh("mesh").feature("size").set("custom","on");
    m.component("c").mesh("mesh").feature("size").set("hmax","40[um]");
    m.component("c").mesh("mesh").feature("size").set("hmin","10[nm]");
    m.component("c").mesh("mesh").feature("size").set("hgrad","1.15");
    m.component("c").mesh("mesh").feature("ft").create("s1","Size");
    m.component("c").mesh("mesh").feature("ft").feature("s1").selection().geom("g",1);
    m.component("c").mesh("mesh").feature("ft").feature("s1").selection().named("bS");
    m.component("c").mesh("mesh").feature("ft").feature("s1").set("custom","on");
    m.component("c").mesh("mesh").feature("ft").feature("s1").set("hmaxactive",true);
    m.component("c").mesh("mesh").feature("ft").feature("s1").set("hmax","50[nm]");
    m.component("c").mesh("mesh").feature("ft").create("s2","Size");
    m.component("c").mesh("mesh").feature("ft").feature("s2").selection().geom("g",1);
    m.component("c").mesh("mesh").feature("ft").feature("s2").selection().named("bG");
    m.component("c").mesh("mesh").feature("ft").feature("s2").set("custom","on");
    m.component("c").mesh("mesh").feature("ft").feature("s2").set("hmaxactive",true);
    m.component("c").mesh("mesh").feature("ft").feature("s2").set("hmax","50[nm]");
    m.component("c").mesh("mesh").run();

    m.study().create("std"); m.study("std").create("stat","Stationary");
    m.study("std").run();
    m.result().numerical().create("gq","EvalGlobal");
    m.result().numerical("gq").set("expr",new String[]{"es.Q0_1"});
    double q=m.result().numerical("gq").getReal()[0][0];
    System.out.println(String.format(Locale.US,"RAIL8 ws_um=%.1f g_um=%.1f wg_um=%.1f vac=%b C_pF_per_mm=%.6f n_elem=%d",
      ws*1e6,g*1e6,wg*1e6,vac,q*1e12*1e-3,m.component("c").mesh("mesh").getNumElem()));
    ModelUtil.remove("M8");
  }
  static String f(double v){ return String.format(Locale.US,"%.6f",v); }
  static void rect(GeomSequence g,String t,double x,double y,double w,double h){
    g.create(t,"Rectangle");
    g.feature(t).set("size",new String[]{String.format(Locale.US,"%.12e",w),String.format(Locale.US,"%.12e",h)});
    g.feature(t).set("pos",new String[]{String.format(Locale.US,"%.12e",x),String.format(Locale.US,"%.12e",y)});
  }
  static void box(Model m,String t,int dim,double xa,double xb,double ya,double yb){
    m.component("c").selection().create(t,"Box");
    m.component("c").selection(t).set("entitydim",""+dim);
    m.component("c").selection(t).set("condition","inside");
    m.component("c").selection(t).set("xmin",String.format(Locale.US,"%.12e",xa)); m.component("c").selection(t).set("xmax",String.format(Locale.US,"%.12e",xb));
    m.component("c").selection(t).set("ymin",String.format(Locale.US,"%.12e",ya)); m.component("c").selection(t).set("ymax",String.format(Locale.US,"%.12e",yb));
  }
}
