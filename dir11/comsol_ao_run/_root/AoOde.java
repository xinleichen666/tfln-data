import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.PrintWriter;
import java.io.StringWriter;

/** Part 1 of the acousto-optic shifter: global ODEs, strict 3.75 ps steps. */
public class AoOde {

  public static Model run() {
    Model model = ModelUtil.create("Model");
    try {
      return build(model);
    } catch (Throwable ex) {
      StringWriter sw = new StringWriter();
      ex.printStackTrace(new PrintWriter(sw));
      model.comments(sw.toString());
      return model;
    }
  }

  public static Model build(Model model) throws Exception {
    model.modelPath("D:\\comsol_ao_run");
    model.label("ao_global_ode.mph");
    model.comments("Ideal AO operating point from Eq. (1), s = 0.");

    model.param().set("fa", "3.33[GHz]");
    model.param().set("Omega", "2*pi*fa");
    model.param().set("mu", "Omega/2");
    model.param().set("gamma", "2*pi*0.6[GHz]");
    model.param().set("kappai", "2*pi*80.75[MHz]");
    model.param().set("Delta", "mu");
    model.param().set("domega", "2*pi*0.55[GHz]");
    model.param().set("ain", "1");
    model.param().set("G1", "(gamma+kappai)/2");
    model.param().set("G2", "kappai/2");
    model.param().set("sqg", "sqrt(gamma)");
    model.param().set("t1", "20[ns]");
    model.param().set("tend", "40[ns]");

    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").feature().create("sq1", "Square");
    model.geom("geom1").feature("sq1").set("size", "1e-6");
    model.geom("geom1").run();

    model.variable().create("var1");
    model.variable("var1").set("Dt", "Delta+domega*cos(Omega*t)");
    model.variable("var1").set("Pm1", "m1r^2+m1i^2");
    model.variable("var1").set("P0", "c0r^2+c0i^2");
    model.variable("var1").set("P1", "c1r^2+c1i^2");
    model.variable("var1").set("P2", "c2r^2+c2i^2");
    model.variable("var1").set("eta", "P1/(Pm1+P0+P1+P2)");
    model.variable("var1").set("dB0", "10*log10(P0/P1)");
    model.variable("var1").set("dBm1", "10*log10(Pm1/P1)");
    model.variable("var1").set("dB2", "10*log10(P2/P1)");

    model.physics().create("ge", "GlobalEquations", "geom1");
    String[] names = {
      "x1", "y1", "x2", "y2",
      "m1r", "m1i", "c0r", "c0i", "c1r", "c1i", "c2r", "c2i"
    };
    String[] eqs = {
      "x1t-(-G1*x1+Dt*y1+mu*y2-sqg*ain)",
      "y1t-(-G1*y1-Dt*x1-mu*x2)",
      "x2t-(-G2*x2+Delta*y2+mu*y1)",
      "y2t-(-G2*y2-Delta*x2-mu*x1)",
      "m1rt-(t>t1)*((ain+sqg*x1)*cos(Omega*t)-(sqg*y1)*sin(Omega*t))",
      "m1it-(t>t1)*((sqg*y1)*cos(Omega*t)+(ain+sqg*x1)*sin(Omega*t))",
      "c0rt-(t>t1)*(ain+sqg*x1)",
      "c0it-(t>t1)*(sqg*y1)",
      "c1rt-(t>t1)*((ain+sqg*x1)*cos(Omega*t)+(sqg*y1)*sin(Omega*t))",
      "c1it-(t>t1)*((sqg*y1)*cos(Omega*t)-(ain+sqg*x1)*sin(Omega*t))",
      "c2rt-(t>t1)*((ain+sqg*x1)*cos(2*Omega*t)+(sqg*y1)*sin(2*Omega*t))",
      "c2it-(t>t1)*((sqg*y1)*cos(2*Omega*t)-(ain+sqg*x1)*sin(2*Omega*t))"
    };
    for (int i = 0; i < names.length; i++) {
      model.physics("ge").feature("ge1").setIndex("name", names[i], i);
      model.physics("ge").feature("ge1").setIndex("equation", eqs[i], i);
      model.physics("ge").feature("ge1").setIndex("initialValueU", "0", i);
      model.physics("ge").feature("ge1").setIndex("initialValueUt", "0", i);
    }

    model.study().create("std1");
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("tlist", "range(0,3.75[ps],tend)");
    model.study("std1").feature("time").set("rtol", "1e-6");
    model.study("std1").createAutoSequences("all");

    model.sol("sol1").feature("t1").set("tstepsbdf", "strict");
    model.sol("sol1").feature("t1").set("maxstepconstraintbdf", "const");
    model.sol("sol1").feature("t1").set("maxstepbdf", "3.75[ps]");
    model.sol("sol1").feature("t1").set("rtol", "1e-6");

    System.out.println("SOLVE_START");
    model.sol("sol1").runAll();
    System.out.println("SOLVE_DONE");

    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("data", "dset1");
    String[] expr = {"eta", "dB0", "dBm1", "dB2", "P0", "P1", "Pm1", "P2", "x1", "y1"};
    for (int i = 0; i < expr.length; i++) {
      model.result().numerical("gev1").setIndex("expr", expr[i], i);
    }
    model.result().numerical("gev1").setIndex("looplevelinput", "last", 0);
    model.result().table().create("tbl1", "Table");
    model.result().numerical("gev1").set("table", "tbl1");
    model.result().numerical("gev1").setResult();
    model.result().table("tbl1").save("D:\\comsol_ao_run\\global_eval.txt");

    try (PrintWriter w = new PrintWriter("D:\\comsol_ao_run\\status.txt", "UTF-8")) {
      w.println("solved");
    } catch (Exception ex) {
      ex.printStackTrace();
    }

    return model;
  }

  public static void main(String[] args) {
    ModelUtil.initStandalone(true);
    Model model = run();
    try {
      model.save("D:\\comsol_ao_run\\ao_global_ode.mph");
    } catch (Exception ex) {
      ex.printStackTrace();
    }
    ModelUtil.disconnect();
  }
}
