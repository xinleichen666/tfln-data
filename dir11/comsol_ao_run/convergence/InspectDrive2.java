import com.comsol.model.*;
import com.comsol.model.util.*;
public class InspectDrive2 {
  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    Model m=ModelUtil.load("m","D:\\comsol_ao_run\\convergence\\Wap_6um_fine_Model.mph");
    for(String p:m.physics().tags()) {
      System.out.println("PHYS "+p+" type="+m.physics(p).getType()+" sel="+java.util.Arrays.toString(m.physics(p).selection().entities()));
      for(String f:m.physics(p).feature().tags()) {
        try { System.out.println(" FEATURE "+p+"."+f+" type="+m.physics(p).feature(f).getType()+" sel="+java.util.Arrays.toString(m.physics(p).feature(f).selection().entities())); } catch(Throwable t) { System.out.println(" FEATURE "+p+"."+f+" "+t); }
      }
    }
    for(String q:m.multiphysics().tags()) {
      System.out.println("MULTI "+q+" type="+m.multiphysics(q).getType()+" sel="+java.util.Arrays.toString(m.multiphysics(q).selection().entities()));
      try { System.out.println(" MULTIPROPS="+java.util.Arrays.toString(m.multiphysics(q).properties())); } catch(Throwable t) {}
    }
    for(String g:m.component("comp1").material("matLN").propertyGroup().tags()) {
      System.out.println("MATGROUP "+g+" "+java.util.Arrays.toString(m.component("comp1").material("matLN").propertyGroup(g).properties()));
      for(String prop:m.component("comp1").material("matLN").propertyGroup(g).properties()) {
        try { System.out.println(" MATPROP "+g+"."+prop+"="+java.util.Arrays.deepToString(m.component("comp1").material("matLN").propertyGroup(g).getStringArray(prop))); } catch(Throwable t) {}
      }
    }
    for(String s:new String[]{"selLN","selAl","selGp","selGn","selGnd"}) {
      try { System.out.println("SELECTION "+s+" dim="+m.component("comp1").selection(s).getInt("entitydim")+" ents="+java.util.Arrays.toString(m.component("comp1").selection(s).entities())); } catch(Throwable t) {}
    }
    ModelUtil.disconnect();
  }
}
