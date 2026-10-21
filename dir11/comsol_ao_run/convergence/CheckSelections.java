import com.comsol.model.*; import com.comsol.model.util.*;
public class CheckSelections {
 public static void main(String[] a)throws Exception {
  ModelUtil.initStandalone(true);
  Model m=ModelUtil.load("m","D:\\comsol_ao_run\\convergence\\Wap_6um_fine_Model.mph");
  for(String s:new String[]{"selGp","selGn"}) {
   System.out.println("before "+s+" "+java.util.Arrays.toString(m.component("comp1").selection(s).entities()));
   m.component("comp1").selection(s).set("condition","inside");
   System.out.println("after "+s+" "+java.util.Arrays.toString(m.component("comp1").selection(s).entities()));
  }
  int[] gp=m.component("comp1").selection("selGp").entities(), gn=m.component("comp1").selection("selGn").entities();
  java.util.Set<Integer> x=new java.util.HashSet<>(); for(int i:gp)x.add(i);
  java.util.List<Integer> overlap=new java.util.ArrayList<>(); for(int i:gn)if(x.contains(i))overlap.add(i);
  System.out.println("overlap="+overlap);
  m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_selectioncheck.mph");
  ModelUtil.disconnect();
 }
}
