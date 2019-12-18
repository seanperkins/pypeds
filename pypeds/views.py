# layer above ETL framework - views are tasks to build specific datasets
import pandas as pd
from dfply import *
from pypeds import ipeds
from pypeds import datasets


#================================================== migration dataset
## the migration data, with school and residence region data appended
def view_migration(years=[2018],
                   efc_line = list(range(1,99)),
                   efc_cols = ['unitid', 'fall_year', 'line', 'efres02 '],
                   hd_deg4yr = True,
                   hd_service = True,
                   hd_lower48 = None,
                   hd_cols = ['unitid', 'fall_year', 'instnm', 'fips', 'obereg', 'sector', 'latitude', 'longitud']):
  """
  Build a migration dataset, with common data mappings using the lower
  level API.

  Parameters:
      years (list): a list of integers for the years to include for the migration data
      efc_line (list): a list of integers representing the values for the line field in efc
      efc_cols (list): a list of valid column names from the efc survey to keep
      hd_deg4yr (bool): boolean (default = True) as to filter to only include degree-granting 4-year institutions
      hd_service (bool): boolean (default = True) which if True, will remove US service schools
      hd_lower48 (bool): boolean (default = None) while if True, will only keep lower 48 states
      hd_cols (list): a list of valid column names for the HD survey.  Only these columns will be returned.
  """
  
  # get the migration data for the years parameter
  m = ipeds.EFC(years=years)
  m.extract()
  m.transform(line=efc_line)
  m.transform(cols=efc_cols)
  m = m.load()
  
  # get the inst data
  i = ipeds.HD(years=years)
  i.extract()
  i.transform(deg4yr=hd_deg4yr)
  i.transform(service=hd_service)
  i.transform(lower_us=hd_lower48)
  i.transform(cols=hd_cols)
  inst = i.load()
  
  # the region dataset
  r = datasets.region_xwalk()
  
  # join the inst data onto migration
  # inner join to keep the school filters
  df = pd.merge(left=m, right=inst, on=['unitid','fall_year'], how='inner')
  
  # merge on data about the school region
  r1 = r >> select(['fips', 'name', 'ipeds_region'])
  df = pd.merge(left=df, right=r1, left_on='fips', right_on='fips', how='left')
  
  # merge on the region info about the state of residence
  r2 = r >> select(['ipeds_code', 'name', 'ipeds_region', 'region', 'division'])
  df = pd.merge(left=df, right=r2, left_on='line', right_on='ipeds_code', how='left', suffixes=['_inst', '_state'])
  
  # return the data
  return (df)



#================================================== discounting dataset
## the migration data, with school and residence region data appended
