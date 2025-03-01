function addField(sectionId, placeholder1, placeholder2) {
    const container = document.getElementById(sectionId);
    const div = document.createElement('div');
    div.classList.add('dynamic-field');
    div.innerHTML = `
        <input type="text" placeholder="${placeholder1}" name="${sectionId}[]" class="input-field" required>
        <input type="number" placeholder="${placeholder2}" name="${sectionId}_weight[]" class="weight-field" required min="0" max="5">
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(div);
}

function addSpecificDegreeField() {
    const container = document.getElementById('specific-degree-section');
    const div = document.createElement('div');
    div.classList.add('dynamic-field');
    div.innerHTML = `
        <input type="text" placeholder="Specific Degree" name="education_specific[]" class="input-field" required>
        <input type="number" placeholder="Weight (0-5)" name="education_specific_weight[]" class="weight-field" required min="0" max="5">
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(div);
}

function addFallbackDegreeField() {
    const container = document.getElementById('fallback-degree-section');
    const div = document.createElement('div');
    div.classList.add('dynamic-field');
    div.innerHTML = `
        <select name="fallback_degree[]" class="input-field">
            <option value="phd">PhD</option>
            <option value="masters">Masters</option>
            <option value="bachelors">Bachelors</option>
        </select>
        <input type="number" placeholder="Weight (0-5)" name="fallback_weight[]" class="weight-field" required min="0" max="5">
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(div);
}

window.onload = function () {
    addField('skills-section', 'Skill', 'Weight (0-5)');
    addSpecificDegreeField();
    addFallbackDegreeField();
    addField('places-section', 'Company Name', 'Weight (0-5)');
}

