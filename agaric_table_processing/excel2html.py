import pandas as pd 

"""
cleans df and makes into html
"""

#Keys to be processed
to_be_expanded = ['Exact Spore Print Colour', 'Habitat', 'Size', 'Gill Attachment', 'Partial Veil', 'Cap Features', 'Stipe Features']

filename = './data.xlsx'

df = pd.read_excel(filename)

#--------------------------------Functions----------------------------------------------

def create_colour_1(row): #Create a second, more vague, spore print colour column
	if row['Exact Spore Print Colour'] == 'White' or row['Exact Spore Print Colour'] == 'Cream' or row['Exact Spore Print Colour'] == 'Buff':
		return 'Pale'
	if 'Brown' in row['Exact Spore Print Colour']:
		return 'Brown'
	if 'Black' in row['Exact Spore Print Colour']:
		return 'Dark (non-brown)'
	if 'Pink' in row['Exact Spore Print Colour']:
		return 'Pink'
	else:
		return 'Other'

#----------------------------------------------------------------------------------------

#Clean:
# df = df.drop(['Is this cross checked with species / done?'], axis=1)

df['Habitat Description'] = df['Habitat Description'].fillna(" n/a ")
df['Gill Description'] = df['Gill Description'].fillna(" n/a ")
df['Cap Description'] = df['Cap Description'].fillna(" n/a ")
df['Stipe Description'] = df['Stipe Description'].fillna(" n/a ")
df['Additional Features of Note'] = df['Additional Features of Note'].fillna(" n/a ")

df['Cap Features'] = df['Cap Features'].fillna('None')
df['Stipe Features'] = df['Stipe Features'].fillna('None')
# df['Top Five NE Species'] = df['Top Five NE Species'].replace(r'\n', ', ', regex=True)

#Combine key columns with description columns so users have full information. 
df['Habitat Description'] = df['Habitat'] + ' | ' + df['Ecology'] + ' | ' + df['Habitat Description'] 
df['Gill Description'] = df['Gill Attachment'] + ' | ' + df['Gill Description']
df['Cap Description'] = df['Cap Features'] + ' | ' + df['Cap Description']
df['Stipe Description'] = df['Stipe Features'] + ' | ' + df['Stipe Description']
df['Additional Features of Note'] = df['Size'] + ' | Veil: ' + df['Partial Veil'] + ' | ' + df['Additional Features of Note']

#Spore Print Description Column
df['Spore Print Colour Description'] = df['Exact Spore Print Colour']

for row in to_be_expanded: #Expand needed rows
	df[row] = df[row].str.strip()
	df[row] = df[row].str.split(' / ')
	df = df.explode(row)


#Create Spore Print Colour 2
df['Exact Spore Print Colour'] = df['Exact Spore Print Colour'].astype(str)
df['General Spore Print Colour'] = df.apply(create_colour_1, axis=1)

#Reorder some columns 
df = df[['Genus Name', 'Spore Print Colour Description', 'General Spore Print Colour', 'Exact Spore Print Colour', 'Habitat',
   'Habitat Description', 'Size', 'Cap Features', 
   'Cap Description', 'Partial Veil', 'Gill Description',
   'Gill Attachment', 'Stipe Features', 'Stipe Description',
   'Additional Features of Note', 'Similar Genera / Look-alikes',
   'NE Genus Species Included' ]]

# df = df.drop(columns=['Spore Print Colour 2', 'Habitat', 'Cap Features', 'Stipe Features'])

df.to_html('processeddataEXP.html', index=False)

print(df)

# quit()

#df.to_excel('./results/ProcessedCheatSheet4.2.xlsx', sheet_name='Data')





df = pd.read_html('processeddataEXP.html')
df = df[0]

key_columns = ['General Spore Print Colour', 'Exact Spore Print Colour', 'Habitat', 'Size', 'Cap Features', 'Partial Veil', 'Gill Attachment', 'Stipe Features']

#-----------Functions------------------------------------------

def column_names(key_columns):
	
	filters_list = []

	for key in key_columns:
		name = df[key].unique()
		filters_list.append(name)

	return filters_list

def write_filter(file, filter_name, key_columns, o):

	
	file.write('\t<div id="list1" class="dropdown-check-list" tabindex="100">\n')
	file.write('\t\t<span class="anchor">' + filter_name + '</span>\n')
	file.write('\t\t<ul class="items">\n')
	file.write('\t\t\t<li><label>Select All ' + str(o) + '<input onClick="toggle(this, ' + "'option" + str(o) + "'" + ')" class=' + "'option" + str(o) + "'" + ' type="checkbox" value="Select All (Key ' + str(o) + ')" checked/></label></li>\n')
	file.write('\t\t\t<li><label>----------</label></li>\n')

	for i in key_columns:

		i = str(i)
		file.write('\t\t<li><label>' + i + " " + str(o) + '<input class="option' + str(o) + '" type="checkbox" value="' + i + " " + str(o) + '" checked/></label></li>\n')

	file.write('\t</ul>\n</div>\n')

#-----------------------------------------------------------

filters_list = column_names(key_columns)

f = open('processeddataEXP.html', "r")
data = f.readlines()

with open('processed_htmlEXP.html', 'w') as new_file:

	new_file.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n
    <title>Table with Filters</title>
    <link rel="stylesheet" href="style.css">
</head>\n\n''')

	new_file.write('<div id="filter-container">')
    
	o = 1
	for i in range(len(key_columns)):
		write_filter(new_file, key_columns[i], filters_list[i], o)
		o += 1

	new_file.write('</div>\n')

	#Add classes to <td>
	td_count = 0

	for d in data:
		print(d)


		if d[0:6] == '<table':
			new_line = d[:6] + ' id="fungi"' + d[6:]
			new_file.write(new_line)

		
		elif d[6:10] == '<td>':
			td_count += 1
			# 3, 4, 5, 7, 8, 10, 12, 13, 
			if td_count == 3:
				new_line = d[:9] + ' class="check1"' + d[9:]
				new_line = new_line[:-6] + ' 1' + d[-6:]
				new_file.write(new_line)

			elif td_count == 4:
				new_line = d[:9] + ' class="check2"' + d[9:]
				new_line = new_line[:-6] + ' 2' + d[-6:]
				new_file.write(new_line)

			elif td_count == 5:
				new_line = d[:9] + ' class="check3"' + d[9:]
				new_line = new_line[:-6] + ' 3' + d[-6:]
				new_file.write(new_line)

			elif td_count == 7:
				new_line = d[:9] + ' class="check4"' + d[9:]
				new_line = new_line[:-6] + ' 4' + d[-6:]
				new_file.write(new_line)

			elif td_count == 8:
				new_line = d[:9] + ' class="check5"' + d[9:]
				new_line = new_line[:-6] + ' 5' + d[-6:]
				new_file.write(new_line)

			elif td_count == 10:
				new_line = d[:9] + ' class="check6"' + d[9:]
				new_line = new_line[:-6] + ' 6' + d[-6:]
				new_file.write(new_line)

			elif td_count == 12:
				new_line = d[:9] + ' class="check7"' + d[9:]
				new_line = new_line[:-6] + ' 7' + d[-6:]
				new_file.write(new_line)

			elif td_count == 13:
				new_line = d[:9] + ' class="check8"' + d[9:]
				new_line = new_line[:-6] + ' 8' + d[-6:]
				new_file.write(new_line)

			elif td_count == 17:
				new_line = d[:10] + '<a target="_blank" rel="noopener noreferrer" href="' + d[10:-6] + '">iNat Species Link</a>' + d[-6:]
				new_file.write(new_line)

			else:
				new_file.write(d)

			if td_count == 17:
				td_count = 0

		else:
			new_file.write(d)

	new_file.write('''\n\n
<script>
var unchecked = [];

function filter(event, filterCol, unchecked) { //to filter HTML table
  let element = event.target; 
  var table = document.getElementById("fungi");
  let filterColumns = ["check1", "check2", "check3", "check4", "check5", "check6", "check7", "check8"]

  if(element.value.includes("Select All")) { // Include the selectall checkbox

    var temp = []
    let condt2 = document.getElementsByClassName(filterCol);
    let condt_unique

    for(var i = 0; i < condt2.length; i++){
      temp.push(condt2[i].innerHTML)
    }

    condt_unique = [...new Set(temp)]

    if (element.checked == true) { // update unchecked array
      for(var i = 0; i < condt_unique.length; i++){
        const index = unchecked.indexOf(condt_unique[i]);
        if (index > -1) { // only splice array when item is found
          unchecked.splice(index, 1); // 2nd parameter means remove one item only
        }
      }
    }
    else  {
      for(var i = 0; i < condt_unique.length; i++){
        if (unchecked.includes(condt_unique[i]) == false)
        unchecked.push(condt_unique[i])
      }
    }
  }

  if (element.checked == true) { // update unchecked array
      const index = unchecked.indexOf(element.value);
      if (index > -1) { // only splice array when item is found
        unchecked.splice(index, 1); // 2nd parameter means remove one item only
      }
    }
    else {
      unchecked.push(element.value)
    }

  for (var i = 0, row; row = table.rows[i]; i++) {
    row.style = "display:table-row"
  }

  for (let f = 0; f < filterColumns.length; f++){ //the filter portion of function
    let condt1 = document.getElementsByClassName(filterColumns[f]); //gather all filter columns

      for (let i = 0; i < condt1.length; i++) {

        if (unchecked.includes(String(condt1[i].innerHTML))) { //if value is unchecked... hide it

          condt1[i].parentElement.closest('tr').style = "display:none" 

        }
      }
  } 

  var unique_arr = document.querySelectorAll("#fungi tbody tr"); //collect rows to iterate through
  var save_one = 0
  var cell_value

  for(var i = 0, row; row = table.rows[i]; i++){ //Hide all non-unique rows that are displayed
    const display = window.getComputedStyle(row).display;

    if(display == "table-row"){
      if(row.cells[1].innerHTML == cell_value && save_one != 1){
        row.style = "display:none"
      }
      cell_value = row.cells[1].innerHTML
    }
  } 

  console.log(unchecked)
}

document.querySelectorAll('.option1').forEach(input => input.addEventListener('input', ()=>filter(event,"check1", unchecked)));
document.querySelectorAll('.option2').forEach(input => input.addEventListener('input', ()=>filter(event,"check2", unchecked)));
document.querySelectorAll('.option3').forEach(input => input.addEventListener('input', ()=>filter(event,"check3", unchecked)));
document.querySelectorAll('.option4').forEach(input => input.addEventListener('input', ()=>filter(event,"check4", unchecked)));
document.querySelectorAll('.option5').forEach(input => input.addEventListener('input', ()=>filter(event,"check5", unchecked)));
document.querySelectorAll('.option6').forEach(input => input.addEventListener('input', ()=>filter(event,"check6", unchecked)));
document.querySelectorAll('.option7').forEach(input => input.addEventListener('input', ()=>filter(event,"check7", unchecked)));
document.querySelectorAll('.option8').forEach(input => input.addEventListener('input', ()=>filter(event,"check8", unchecked)));


let checkLists = document.getElementsByClassName('dropdown-check-list'); //Allows checkboxes to open, and be used

for(let i = 0; i < checkLists.length; i++) {
  let checkList = checkLists[i];

  checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
    if (checkList.classList.contains('visible'))
      checkList.classList.remove('visible');
    else
      checkList.classList.add('visible');
  }
}

var table = document.getElementById("fungi");
var unique_arr = document.querySelectorAll("#fungi tbody tr");
var cell_value
for(var i = 0, row; row = table.rows[i]; i++){ //makes all rows unique
  if(row.cells[1].innerHTML == cell_value){
    row.style = "display:none"
  }
  cell_value = row.cells[1].innerHTML
}

function toggle(source, clss) {

checkboxes = document.getElementsByClassName(clss);
for(var i = 0; i < checkboxes.length; i++)
  checkboxes[i].checked = source.checked;
}
</script>

	''')

print(df.columns)