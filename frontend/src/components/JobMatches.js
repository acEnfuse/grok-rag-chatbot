import React from 'react';

const JobMatches = ({ matches, cvData }) => {

  const getMatchScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Low Match';
  };

  return (
    <div>
      {matches && matches.length > 0 ? (
        <div className="space-y-6">
          {matches.map((job, index) => (
            <div key={job.id || index}>
              <div className="bg-white rounded-lg shadow p-6" style={{paddingLeft: '24px', paddingRight: '24px'}}>
                <div className="mb-2">
                {index === 0 && <br/>}
                <div className="text-gray-800 mb-4" style={{fontSize: '24px', fontWeight: 'bold'}}>
                  {job.job_title || 'Job Title Not Available'}
                </div>
                <div className="text-gray-600 mb-1">
                  <strong>Sector:</strong> {job.company || 'Company Not Specified'}
                </div>
                <div className="text-gray-600 mb-1">
                  <strong>Match Percentage:</strong> {job.match_score}% Match
                </div>
                <div className="text-gray-600">
                  <strong>Match Level:</strong> {getMatchScoreLabel(job.match_score)}
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 text-gray-600">
                <div>
                  <strong>Location:</strong> {job.location || 'Not specified'}
                </div>
                
                {job.salary_range && (
                  <div>
                    <strong>Salary:</strong> {job.salary_range}
                  </div>
                )}
              </div>

              <div>
                <div className="text-gray-800 mb-2"><strong>Description:</strong></div>
                <p className="text-gray-600 leading-relaxed">
                  {job.description || 'No description available'}
                </p>
              </div>

              {job.required_skills && (
                <div>
                  <div className="text-gray-800 mb-2"><strong>Required Skills:</strong></div>
                  {console.log('🔍 RAW SKILLS STRING:', job.required_skills)}
                  {console.log('🔍 SPLIT RESULT:', job.required_skills.split(','))}
                  <div style={{lineHeight: '1.4'}}>
                    {job.required_skills.split(',').map(s => s.trim()).filter(s => s.length > 0).join(', ')}
                  </div>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4 text-gray-600">
                {job.experience_level && (
                  <div>
                    <strong>Experience Level:</strong> {job.experience_level}
                  </div>
                )}
                
                {job.education_requirements && (
                  <div>
                    <strong>Education:</strong> {job.education_requirements}
                  </div>
                )}
              </div>
              </div>
              {index < matches.length - 1 && (
                <div className="mt-6 mb-6">
                  <div style={{backgroundColor: '#10412A', height: '4px', width: '100%'}}></div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="bg-white p-8 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              No Job Matches Found
            </h3>
            <p className="text-gray-500">
              We couldn't find any matching job opportunities at the moment.
              Try uploading a different CV or check back later.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobMatches;
