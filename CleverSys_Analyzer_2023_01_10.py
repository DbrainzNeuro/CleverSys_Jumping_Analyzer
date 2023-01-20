#!/usr/bin/env python
# coding: utf-8

# In[7]:


# set up the App: Fill in info here, then run next cells

import pandas as pd
from datetime import timedelta
import datetime as datetime
from datetime import datetime as dt
from ipyfilechooser import FileChooser
import ipywidgets as widgets
from ipywidgets import AppLayout
import glob
pd.options.mode.chained_assignment = None


# set up GUI
# Create and display a FileChooser widgets
fc_processed = FileChooser()
fc_processed.show_only_dirs = True
fc_processed.title = '<b>Locate the folder containing your raw .csv files</b>'

fc_saver = FileChooser()
fc_saver.show_only_dirs = True
fc_saver.title = '<b> Where do you want your outputs saved?: NOTE they must be alone in a folder for the next step of processing, so create a new folder for them to be in first </b>'


final_save = widgets.Text(
    value='Enter Final Save Name',
    placeholder='Type something',
    description='',
    disabled=False
)


header0 = widgets.Label(value= "Requirements:")
header00 = widgets.Label(value= "Cleversys output files consisting of 48 30-minute blocks of behavior with all behaviors selected for output")
header000 = widgets.Label(value= "Make sure to check the box for interleaved data so the columns are Mouse 1 time, then Mouse 1 duration, etc, not all time then all durations.")
header0000 = widgets.Label(value= "All mice used must have a value in their mouse number info spot at Row 9 cells B,C,D,E in your excel output")
header00000 = widgets.Label(value = "Date and Time must be in cell 20B in the format YYYY-MM-DD HH:MM:SS")



header = widgets.Label(
    value="Program Instructions:")
header1 = widgets.Label("Locate your raw data files (ALL .csv files in the selected folder will be processed")
header2 = widgets.Label(value="Then locate an EMPTY folder for your outputs.")
header3 = widgets.Label(value="Finally, name your output file.")
spacer = widgets.Label(value="    ")
saveinstructions = widgets.Label(
    value="Enter the name you want to save the final file as.")
finder = widgets.VBox([header0,header00,header000, header0000, header00000,spacer,header, header1, header2, header3, spacer, fc_processed,
                      spacer, fc_saver, spacer, saveinstructions, final_save])


finder
# deploy GUI


# In[ ]:


# Define all Functions
# Before you run the rest of the function definitions, change the savename info to wherever you want your outputs saved to

# save it
def saveit(dark, MasterFile0, summary):
    date = str(dark['Start Time'].values[0])[:10]
    savename = str(fc_saver.selected_path) + "\\" + " " + date +         " Processed " + str(dt.today().strftime('%Y-%m-%d')) + ".xlsx"

# modify for excel writing
    dark[['Behavior', 'Bin No', 'Start Time', 'Sex', 'Genotype', 'Start']] = dark[[
        'Behavior', 'Bin No', 'Start Time', 'Sex', 'Genotype', 'Start']].astype(str)
    MasterFile0[['Behavior', 'Bin No', 'Start Time', 'Sex', 'Genotype', 'Start']] = MasterFile0[[
        'Behavior', 'Bin No', 'Start Time', 'Sex', 'Genotype', 'Start']].astype(str)

    with pd.ExcelWriter(savename) as writer:
        dark.to_excel(writer, sheet_name='Dark')
        MasterFile0.to_excel(writer, sheet_name='All Data')
        summary.to_excel(writer, sheet_name='Sum in Dark')
    return(savename)


# remaining functions


def analyze_cleversys(xls, mouse1, mouse2, mouse3, m1geno, m2geno, m3geno,
                      m1sex, m2sex, m3sex):
    # import info
    names_and_dates = pd.read_excel(xls, 'HCSInfo')
    data = pd.read_excel(xls, 'HCSGrpBinTimesDuration')

    # make the numbers numeric
    x = range(2, len(data.columns), 1)
    for n in x:
        data.iloc[:, n] = pd.to_numeric(data.iloc[:, n], errors='coerce')

    data2 = data.drop([0, 1, 2, 3, 4, 5], axis=0).fillna(method='ffill')

    mice = [mouse1, mouse2, mouse3, mouse4]
    mice = [i for i in mice if i != 0]
    num_mice = len(mice)
    print(num_mice, " mice")

# if there are 4 mice
    if num_mice == 4:
        data2.columns = [
            'Behavior', 'Bin No', 'Mouse 1 Times', 'Mouse 1 Duration',
            'Mouse 2 Times', 'Mouse 2 Duration', 'Mouse 3 Times',
            'Mouse 3 Duration', 'Mouse 4 Times', 'Mouse 4 Duration'
        ]
        print("4 mice,", data2.columns)
        data2.to_clipboard()

# if there are 3 mice
    if num_mice == 3:
        data2 = data2.iloc[:, :8]
        print(len(data2.columns))
        data2.columns = [
            'Behavior', 'Bin No', 'Mouse 1 Times', 'Mouse 1 Duration',
            'Mouse 2 Times', 'Mouse 2 Duration', 'Mouse 3 Times',
            'Mouse 3 Duration'
        ]
        print("3 mice,", data2.columns)

# if there are 2 mice
    if num_mice == 2:
        data2 = data2.iloc[:, :6]
        data2.columns = [
            'Behavior', 'Bin No', 'Mouse 1 Times', 'Mouse 1 Duration',
            'Mouse 2 Times', 'Mouse 2 Duration'
        ]
        print("2 mice,", data2.columns)

# if there is 1 mouse
    if num_mice == 1:
        data2 = data2.iloc[:, :4]
        data2.columns = [
            'Behavior', 'Bin No', 'Mouse 1 Times', 'Mouse 1 Duration'
        ]
        print("1 mouse,", data2.columns)

# filter behaviors
    data3 = data2[data2['Behavior'].isin([
        'Groom', 'HVfromHC', 'HVfromRU', 'HangCudl', 'Jump', 'Pause', 'RearUp',
        'RemainHC', 'RemainHV', 'RemainLw', 'RemainPR', 'RemainRU', 'ReptJump',
        'Sleep', 'Stationa', 'Stretch', 'TravDist.', 'Turn'
    ])]


# get start times sorted out
    start0 = names_and_dates.iloc[18:19, 1:2]
    val = start0['Unnamed: 1'].values[0]

    dstart = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
    starts, starts1 = [], []
    starts.append(dstart)
    for i in range(0, 47):
        starts.append(starts[i] + timedelta(minutes=30))

    for time in range(0, (len(starts))):
        starts[time] = starts[time].strftime('%Y-%m-%d %H:%M:%S')

    all_start = starts * len(set(data3['Behavior']))

    data3['Start Time'] = all_start

# split into one dataframe per mouse

    Mdf = data3[[
        'Behavior', 'Bin No', 'Mouse 1 Times', 'Mouse 1 Duration', 'Start Time'
    ]].copy()

    Mdf['Mouse'] = mouse1
    Mdf['Sex'] = m1sex
    Mdf['Genotype'] = m1geno
    Mdf.rename(columns={'Mouse 1 Times': 'Times'}, inplace=True)
    Mdf.rename(columns={'Mouse 1 Duration': 'Duration'}, inplace=True)

    if num_mice >= 2:
        M2df = data3[[
            'Behavior', 'Bin No', 'Mouse 2 Times', 'Mouse 2 Duration', 'Start Time'
        ]].copy()

        M2df['Mouse'] = mouse2
        M2df['Sex'] = m2sex
        M2df['Genotype'] = m2geno
        M2df.rename(columns={'Mouse 2 Times': 'Times'}, inplace=True)
        M2df.rename(columns={'Mouse 2 Duration': 'Duration'}, inplace=True)

    if num_mice >= 3:
        M3df = data3[[
            'Behavior', 'Bin No', 'Mouse 3 Times', 'Mouse 3 Duration', 'Start Time'
        ]].copy()

        M3df['Mouse'] = mouse3
        M3df['Sex'] = m3sex
        M3df['Genotype'] = m3geno
        M3df.rename(columns={'Mouse 3 Times': 'Times'}, inplace=True)
        M3df.rename(columns={'Mouse 3 Duration': 'Duration'}, inplace=True)

    if num_mice == 4:
        M4df = data3[[
            'Behavior', 'Bin No', 'Mouse 4 Times', 'Mouse 4 Duration', 'Start Time'
        ]].copy()

        M4df['Mouse'] = mouse4
        M4df['Sex'] = m4sex
        M4df['Genotype'] = m4geno
        M4df.rename(columns={'Mouse 4 Times': 'Times'}, inplace=True)
        M4df.rename(columns={'Mouse 4 Duration': 'Duration'}, inplace=True)

# put it back together
    if num_mice == 2:
        Mdf = Mdf.append(M2df, ignore_index=True)

    if num_mice == 3:
        Mdf = Mdf.append(M2df, ignore_index=True).append(M3df,
                                                         ignore_index=True)
    if num_mice == 4:
        Mdf = Mdf.append(M2df, ignore_index=True).append(
            M3df, ignore_index=True).append(M4df, ignore_index=True)

    MasterFile0 = Mdf.copy()
# Set the dates up to be usable
    MasterFile0['Start Time'] = pd.to_datetime(MasterFile0['Start Time'],
                                               utc=True)
    MasterFile0['Start'] = [
        datetime.datetime.time(d) for d in MasterFile0['Start Time']
    ]

# put a fake day value in so I can compare across days
    fakedate = str(datetime.datetime.strptime('2000-01-01', '%Y-%m-%d').date())
    MasterFile0['Start'] = pd.to_datetime(fakedate + " " +
                                          MasterFile0['Start'].astype(str))

# Make the values the right types so we can use them
   # MasterFile0[["Times",
    #            "Duration"]] = MasterFile0[["Times",
    #                   "Duration"]].apply(pd.to_numeric)
    MasterFile0['Mouse'] = MasterFile0['Mouse'].astype(str)
    MasterFile0['Start'] = pd.to_datetime(MasterFile0['Start'], utc=True)

# extract times in the dark
    dark = MasterFile0[~((MasterFile0['Start'] > '2000-01-01 06:00:00') &
                         (MasterFile0['Start'] <= '2000-01-01 18:00:00'))]

# get summary data
    summary = dark.drop(columns=['Bin No', 'Start'])
    summary = dark.drop(columns=['Bin No', 'Start']).groupby([
        'Genotype',
        'Behavior',
        'Sex',
        'Mouse',
    ]).agg(['sum', 'mean', 'sem']).reset_index()
    summary.columns = [
        'Genotype', 'Behavior', 'Sex', 'Mouse', 'Sum_Times', 'Mean_Times',
        'SEM_Times', 'Sum_Duration', 'Mean_Duration', 'SEM_Duration'
    ]
    return (dark, MasterFile0, summary)


def pad(l, content, width):
    l.extend([content] * (width - len(l)))
    return l


# In[ ]:


# Process files and save them

# read each file and process it
import warnings
import datetime as datetime
globber = fc_processed.selected_path + "\*.xlsx"
globbed_files = glob.glob(globber)

warnings.simplefilter(action='ignore', category=FutureWarning)

for xl in globbed_files:
    # get each file and parse out the mouse / geno / hemisphere
    names_and_dates = pd.read_excel(xl, 'HCSInfo', index_col=0)
    data = pd.read_excel(xl, 'HCSGrpBinTimesDuration')

    mouse_ids = list(names_and_dates.loc['Mouse ID'])
    pad(mouse_ids, 0, 4)
    mouse_ids = mouse_ids[:4]

    if "Sex" in names_and_dates.index:
        sexes = list(names_and_dates.loc['Sex'])
        pad(sexes, 0, 4)
        sexes = sexes[:4]

    if "Genotype" in names_and_dates.index:
        genos = list(names_and_dates.loc['Genotype'])
        pad(genos, 0, 4)
        genos = genos[:4]

    m1geno = genos[0]
    m2geno = genos[1]
    m3geno = genos[2]
    m4geno = genos[3]

    mouse1 = mouse_ids[0]
    mouse2 = mouse_ids[1]
    mouse3 = mouse_ids[2]
    mouse4 = mouse_ids[3]

    m1sex = sexes[0]
    m2sex = sexes[1]
    m3sex = sexes[2]
    m4sex = sexes[3]

    dark, MasterFile0, summary = analyze_cleversys(
        xl, mouse1, mouse2, mouse3, m1geno, m2geno, m3geno, m1sex, m2sex, m3sex)
    savename = saveit(dark, MasterFile0, summary)



# In[ ]:


# pick up processed files and produce final file
globber2 = fc_saver.selected_path + "\*.xlsx"
globbed_files2 = glob.glob(globber2)

dataframe = pd.DataFrame(
    columns=['Genotype', 'Behavior', 'Sex', 'Mouse', 'Sum_Duration', 'Sum_Times'])

for xl in globbed_files2:
    # get each file
    data = pd.read_excel(xl, 'Sum in Dark', index_col=0)
    data2 = data[['Genotype', 'Behavior', 'Sex',
                  'Mouse', 'Sum_Duration', 'Sum_Times']]
    dataframe = pd.concat([dataframe, data2])


# format the final save file
# empty frame to add to
allmice = pd.DataFrame(columns=['Mouse', 'Groom', 'HVfromHC', 'HVfromRU', 'HangCudl', 'Jump', 'Pause',
                                'RearUp', 'RemainHC', 'RemainHV', 'RemainLw', 'RemainPR', 'RemainRU',
                                'ReptJump', 'Sleep', 'Stationa', 'Stretch', 'TravDist.', 'Turn'])


for m in set(dataframe['Mouse']):
    mouseframe = dataframe[dataframe['Mouse'] == m]

   # remove travel for now
    travelframe = mouseframe[mouseframe['Behavior'] == "TravDist."
                             ]
    travelframe['Sum_Duration'] = travelframe['Sum_Times']

    notravframe = mouseframe[mouseframe['Behavior'] != "TravDist"]
    allframe = pd.concat([travelframe, notravframe], sort=False)

    allmice0 = allframe.pivot_table(index=['Mouse', 'Genotype', 'Sex'], columns='Behavior',
                                    values='Sum_Duration', aggfunc='sum').reset_index()

    allmice = pd.concat([allmice0, allmice], sort=False)


# save the file
saveitt = fc_saver.selected_path + "\\" + str(final_save.value) + ".xlsx"
allmice.to_excel(saveitt)
print("File saved!")

