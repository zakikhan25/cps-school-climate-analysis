/*---------------------------------------------------------------
  CPS School Climate & Attendance Analysis  (SAS version)
  Same question as analysis.py: how are chronic truancy, school
  climate, and school conditions related across CPS schools?

  NOTE: I could not run SAS while building this. Run it in the free
  SAS OnDemand for Academics (or SAS Viya Workbench), check the log
  for errors, and fix any variable-name issues before relying on it.
  If the URL download is blocked, download the CSV from the Chicago
  Data Portal, upload it to SAS, and point DATAFILE at that path.
----------------------------------------------------------------*/

filename cps url
  "https://data.cityofchicago.org/api/views/2dn2-x66j/rows.csv?accessType=DOWNLOAD";

proc import datafile=cps out=work.schools_raw dbms=csv replace;
  guessingrows=max;
run;

/* ---- 1. Clean and recode ---- */
data work.schools;
  set work.schools_raw;

  /* Truancy may import as text or number; VVALUEX handles both */
  truancy = input(strip(vvaluex('Chronic_Truancy_Pct')), ?? best12.);

  /* Ordered scores for text survey ratings; NOT ENOUGH DATA stays missing */
  select (upcase(Culture_Climate_Rating));
    when ('NOT YET ORGANIZED')     climate_score = 1;
    when ('PARTIALLY ORGANIZED')   climate_score = 2;
    when ('MODERATELY ORGANIZED')  climate_score = 3;
    when ('ORGANIZED')             climate_score = 4;
    when ('WELL ORGANIZED')        climate_score = 5;
    otherwise                      climate_score = .;
  end;

  select (upcase(School_Survey_Safety));
    when ('VERY WEAK')   safety_score = 1;
    when ('WEAK')        safety_score = 2;
    when ('NEUTRAL')     safety_score = 3;
    when ('STRONG')      safety_score = 4;
    when ('VERY STRONG') safety_score = 5;
    otherwise            safety_score = .;
  end;
run;

/* ---- 2. Data quality: missing values ---- */
proc means data=work.schools n nmiss min max mean;
  var truancy Student_Attendance_Year_2_Pct Mobility_Rate_Pct
      climate_score safety_score;
  title "Data quality check: counts and missing values";
run;

/* ---- 3. Truancy by school level and type ---- */
proc means data=work.schools n median mean maxdec=1;
  class Primary_Category;
  var truancy Student_Attendance_Year_2_Pct;
  title "Chronic truancy and attendance by school level";
run;

proc means data=work.schools n median maxdec=1;
  class School_Type;
  var truancy;
  title "Chronic truancy by school type";
run;

/* ---- 4. Rank correlations (robust to skew and ordinal scores) ---- */
proc corr data=work.schools spearman;
  var truancy Student_Attendance_Year_2_Pct Mobility_Rate_Pct
      climate_score safety_score;
  title "Spearman correlations";
run;

/* ---- 5. Regression: what is associated with chronic truancy? ---- */
proc glm data=work.schools;
  class Primary_Category;
  model truancy = safety_score climate_score Mobility_Rate_Pct
                  Primary_Category / solution;
  title "Regression: factors associated with chronic truancy";
run;
quit;

/* ---- 6. Chart ---- */
proc sgplot data=work.schools;
  scatter x=safety_score y=truancy / transparency=0.5;
  xaxis label="Student-reported safety (1 = very weak, 5 = very strong)";
  yaxis label="Chronic truancy (%)";
  title "Safety rating vs chronic truancy";
run;
