use "C:\Users\micha\OneDrive\Pulpit\projekt ekonomia nierownosci\regression_data.dta"

gen ln_mln = ln(permln)
gen ln_i10 = ln(i10gini)
gen ln_h = ln(hgini)
gen ln_spn = ln(spending)
gen ln_educ = ln(rd_educ)
gen ln_gov = ln(rd_gov)
gen ln_cit = ln(citations_gini)
gen ln_pop = ln(population)

reg ln_cit ln_educ ln_spn ln_gov ln_pop ln_mln
estimates store ln_cit
estat hettest
estat ovtest
estat vif

reg ln_i10 ln_educ ln_spn ln_gov ln_pop ln_mln
estimates store ln_i10
estat hettest
estat ovtest
estat vif

reg ln_h ln_educ ln_spn ln_gov ln_pop ln_mln
estimates store ln_h
estat hettest
estat ovtest
estat vif

estimates table ln_cit ln_i10 ln_h


reg ln_i10 ln_educ ln_pop
estimates store ln_i10
estat hettest
estat ovtest
estat vif


ivregress 2sls ln_i10 ln_pop (ln_spn = ln_mln)
estat endog
estat firststage
ivregress 2sls ln_i10 ln_pop (ln_educ = ln_mln)
estat endog
estat firststage