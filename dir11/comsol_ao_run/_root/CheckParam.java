import com.comsol.model.*;
import com.comsol.model.util.*;
public class CheckParam {
  public static void main(String[] args) {
    ModelUtil.initStandalone(true);
    try {
      String wap=args.length>0?args[0]:"10";
      Model m=ModelUtil.load("base", "D:\\comsol_ao_run\\idt_3d_sus\\Idt3dSus_Model.mph");
      m.param().set("Wap", wap+"[um]");
      m.param().set("Wstack", "("+wap+"[um]+4[um])");
      m.geom("geom1").run();
      m.mesh("mesh1").run();
      m.study("std1").run();
      m.result().numerical().create("checkFreq", "EvalGlobal");
      m.result().numerical("checkFreq").set("expr", new String[]{"freq"});
      m.result().numerical("checkFreq").set("looplevelinput", new String[]{"all"});
      double[][] r=m.result().numerical("checkFreq").getReal();
      for(int i=0;i<r[0].length;i++) System.out.println(String.format(java.util.Locale.US,"MODE %d f=%.6fGHz",i+1,r[0][i]/1e9));
    } catch(Throwable t) { t.printStackTrace(System.out); }
    ModelUtil.disconnect();
  }
}
