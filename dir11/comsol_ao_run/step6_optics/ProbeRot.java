import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

/** Does the Rotated system on pzm1/ccp1 change the mechanics? Fixed-bottom LN plate, eigenfrequencies for several Euler angle sets. */
public class ProbeRot {
  static final String PZ="D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  public static void main(String[] a){
    try{
      ModelUtil.initStandalone(true);
      String[][] angs={{"0","0","0"},{"90[deg]","0","0"},{"90[deg]","90[deg]","0"},{"0","90[deg]","0"}};
      for(int t=0;t<angs.length;t++){
        Model m=ModelUtil.create("P"+t);
        m.component().create("comp1",true);
        GeomSequence g=m.component("comp1").geom().create("geom1",2);
        g.lengthUnit("um");
        g.create("r1","Rectangle"); g.feature("r1").set("size",new String[]{"2","0.4"}); g.run();
        Model pz=ModelUtil.load("pz",PZ);
        Material ln=m.component("comp1").material().create("matLN","Common"); ln.selection().all();
        copyGroup(ln,pz.material("lithium_niobate"),"def",false); copyGroup(ln,pz.material("lithium_niobate"),"StressCharge",true);
        ModelUtil.remove("pz");
        m.component("comp1").physics().create("solid","SolidMechanics","geom1");
        m.component("comp1").physics().create("es","Electrostatics","geom1");
        m.component("comp1").physics("solid").create("pzm1","PiezoelectricMaterialModel",2); m.component("comp1").physics("solid").feature("pzm1").selection().all();
        m.component("comp1").multiphysics().create("pze1","PiezoelectricEffect","geom1");
        m.component("comp1").physics("es").create("ccp1","ChargeConservationPiezo",2); m.component("comp1").physics("es").feature("ccp1").selection().all();
        m.component("comp1").coordSystem().create("sys2","Rotated");
        String mok="none"; for(String mv:new String[]{"general","euler","eulerAngles","full","rotation"}){ try{ m.component("comp1").coordSystem("sys2").set("method",mv); mok=mv; break; }catch(Throwable e){ System.out.println("METHOD_FAIL "+mv+": "+e.getMessage()); } } System.out.println("METHOD_SET "+mok+" now="+m.component("comp1").coordSystem("sys2").getString("method")); m.component("comp1").coordSystem("sys2").set("rotationSequence","ZXZ"); m.component("comp1").coordSystem("sys2").set("angle",angs[t]);
        m.component("comp1").physics("solid").feature("pzm1").set("coordinateSystem","sys2");
        m.component("comp1").physics("es").feature("ccp1").set("coordinateSystem","sys2");
        if(t==0){
          for(String p:m.component("comp1").coordSystem("sys2").properties()){ String v; try{ v=Arrays.toString(m.component("comp1").coordSystem("sys2").getStringArray(p)); }catch(Throwable e){ try{ v=m.component("comp1").coordSystem("sys2").getString(p); }catch(Throwable e2){ v="?"; } } System.out.println("SYS2PROP "+p+" = "+v); }
          Object f=m.component("comp1").physics("solid").feature("pzm1");
          for(String p:m.component("comp1").physics("solid").feature("pzm1").properties()) if(p.toLowerCase().contains("coord")||p.toLowerCase().contains("sys")) System.out.println("PZMPROP "+p+" = "+m.component("comp1").physics("solid").feature("pzm1").getString(p));
          for(String p:m.component("comp1").physics("es").feature("ccp1").properties()) if(p.toLowerCase().contains("coord")||p.toLowerCase().contains("sys")) System.out.println("CCPPROP "+p+" = "+m.component("comp1").physics("es").feature("ccp1").getString(p));
        }
        m.component("comp1").physics("solid").create("fix1","Fixed",1); m.component("comp1").physics("solid").feature("fix1").selection().set(new int[]{2});
        m.component("comp1").physics("es").create("gnd1","Ground",1); m.component("comp1").physics("es").feature("gnd1").selection().set(new int[]{2});
        m.component("comp1").mesh().create("mesh1"); m.component("comp1").mesh("mesh1").autoMeshSize(4); m.component("comp1").mesh("mesh1").run();
        m.study().create("std1"); m.study("std1").create("eig","Eigenfrequency");
        m.study("std1").feature("eig").set("neigs","6"); m.study("std1").feature("eig").set("shift","1[GHz]"); m.study("std1").feature("eig").set("shiftactive","on");
        m.study("std1").createAutoSequences("all"); m.study("std1").run();
        m.result().numerical().create("gq","EvalGlobal"); m.result().numerical("gq").set("expr",new String[]{"freq","sys2.T11","sys2.T13","sys2.T31","sys2.T12","sys2.T21","sys2.T23","sys2.T32","sys2.T22","sys2.T33"});
        m.result().numerical("gq").set("data","dset1");
        double[][] re=null; String err="";
        try{ re=m.result().numerical("gq").getReal(); }catch(Throwable e){ err=e.getMessage(); m.result().numerical("gq").set("expr",new String[]{"freq"}); re=m.result().numerical("gq").getReal(); }
        StringBuilder sb=new StringBuilder();
        for(int k=0;k<re[0].length;k++) sb.append(String.format(Locale.US," %.6f",re[0][k]/1e9));
        System.out.println("PROBEROT angles="+Arrays.toString(angs[t])+" f_GHz="+sb+(re.length>1?" T11="+re[1][0]+" T12="+re[4][0]+" T13="+re[2][0]+" T21="+re[5][0]+" T22="+re[8][0]+" T23="+re[6][0]+" T31="+re[3][0]+" T32="+re[7][0]+" T33="+re[9][0]:" (sys2.T* n/a: "+err+")"));
        ModelUtil.remove("P"+t);
      }
    }catch(Throwable t){ System.out.println("PROBE_ABORT"); t.printStackTrace(System.out); }
  }
  static void copyGroup(Material d,Material s,String g,boolean c){
    if(c) d.propertyGroup().create(g,g);
    String[] n=s.propertyGroup(g).properties();
    for(int i=0;i<n.length;i++){ try{ d.propertyGroup(g).set(n[i],s.propertyGroup(g).getStringArray(n[i])); }catch(Exception e){} }
  }
}
