import com.comsol.model.*;
import com.comsol.model.util.*;
public class VerifyBase {
  public static void main(String[] args) {
    ModelUtil.initStandalone(true);
    try {
      Model m=ModelUtil.load("base", "D:\\comsol_ao_run\\idt_3d_sus\\Idt3dSus_Model.mph");
      m.study("std1").run();
      m.result().numerical().create("checkFreq", "EvalGlobal");
      m.result().numerical("checkFreq").set("expr", new String[]{"freq","intLN(solid.Ws)","intAl(solid.Ws)","intLN(u^2)","intLN(v^2)","intLN(w^2)"});
      m.result().numerical("checkFreq").set("looplevelinput", new String[]{"all"});
      double[][] r=m.result().numerical("checkFreq").getReal();
      for(int i=0;i<r[0].length;i++) System.out.println(String.format(java.util.Locale.US,"MODE %d f=%.6fGHz eLN=%.4e eAl=%.4e u2=%.4e v2=%.4e w2=%.4e",i+1,r[0][i]/1e9,r[1][i],r[2][i],r[3][i],r[4][i],r[5][i]));
    } catch(Throwable t) { t.printStackTrace(System.out); }
    ModelUtil.disconnect();
  }
}
