"""
Statistical toolkit aimed to help statisticians, data analysts, data scientists, bankers and other professionals to analyze financial data.

Designed by the team of the Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market (ARDFM).

"""

__version__ = "3.0.0"

from AFR.adjr2_score import adjr2_score
from AFR.aic_score import aic_score
from AFR.bic_score import bic_score
from AFR.check_betas import check_betas
from AFR.checkdata import checkdata
from AFR.corsel import corsel
from AFR.dec_plot import dec_plot
from AFR.opt_size import opt_size
from AFR.pt_multi import pt_multi
from AFR.pt_one import pt_one
from AFR.reg_test import reg_test
from AFR.regsel_f import regsel_f
from AFR.sbic_score import sbic_score
from AFR.vif_reg import vif_reg
from AFR.finratKZ import load_finratKZ
from AFR.macroKZ import load_macroKZ

__all__ = ['load_macroKZ', 'load_finratKZ']